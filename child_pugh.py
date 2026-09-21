#!/usr/bin/env python3
"""Child-Pugh-Turcotte score calculator with optional legacy MELD (2001)."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, Optional


def _finite_number(name: str, value: float, *, allow_zero: bool = False) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if value < 0 or (value == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "greater than zero"
        raise ValueError(f"{name} must be {qualifier}")
    return value


def _score_bilirubin(bilirubin_mg_dl: float) -> int:
    if bilirubin_mg_dl < 2.0:
        return 1
    if bilirubin_mg_dl <= 3.0:
        return 2
    return 3


def _score_albumin(albumin_g_dl: float) -> int:
    if albumin_g_dl > 3.5:
        return 1
    if albumin_g_dl >= 2.8:
        return 2
    return 3


def _score_inr(inr: float) -> int:
    if inr < 1.7:
        return 1
    if inr <= 2.3:
        return 2
    return 3


def _normalized(value: str) -> str:
    return " ".join(value.strip().lower().replace("-", " ").replace("_", " ").replace("/", " ").split())


def _score_ascites(ascites: str) -> int:
    value = _normalized(ascites)
    if value in {"none", "no", "absent", "0"}:
        return 1
    if value in {"mild", "controlled", "mild controlled", "slight", "1", "diuretic responsive"}:
        return 2
    if value in {"moderate", "severe", "moderate severe", "moderate to severe", "refractory", "2", "3"}:
        return 3
    raise ValueError("Ascites must be none, mild/controlled, or moderate-severe")


def _score_encephalopathy(encephalopathy: str) -> int:
    value = _normalized(encephalopathy)
    if value in {"none", "no", "absent", "0", "grade 0"}:
        return 1
    if value in {"grade i ii", "grade 1 2", "i ii", "1 2", "grade i", "grade ii", "grade 1", "grade 2", "minimal", "mild", "moderate"}:
        return 2
    if value in {"grade iii iv", "grade 3 4", "iii iv", "3 4", "grade iii", "grade iv", "grade 3", "grade 4", "severe", "coma"}:
        return 3
    raise ValueError("Encephalopathy must be none, grade I-II, or grade III-IV")


def _child_pugh_class(total_score: int) -> str:
    if total_score <= 6:
        return "A"
    if total_score <= 9:
        return "B"
    return "C"


def _class_description(child_class: str) -> str:
    return {
        "A": "Lower Child-Pugh severity class",
        "B": "Intermediate Child-Pugh severity class",
        "C": "Higher Child-Pugh severity class",
    }[child_class]


def _one_year_survival(child_class: str) -> float:
    """Legacy class-level estimate retained for API compatibility; not patient-specific."""
    return {"A": 100.0, "B": 80.0, "C": 45.0}[child_class]


def calculate_meld(
    bilirubin_mg_dl: float,
    inr: float,
    creatinine_mg_dl: float,
    dialysis: bool = False,
) -> Dict[str, Any]:
    """Calculate the legacy 2001 MELD score, not the current OPTN allocation MELD."""
    bilirubin_mg_dl = _finite_number("Bilirubin", bilirubin_mg_dl, allow_zero=False)
    inr = _finite_number("INR", inr, allow_zero=False)
    creatinine_mg_dl = _finite_number("Creatinine", creatinine_mg_dl, allow_zero=False)

    bili = max(bilirubin_mg_dl, 1.0)
    inr_used = max(inr, 1.0)
    creat_used = 4.0 if dialysis else min(max(creatinine_mg_dl, 1.0), 4.0)

    raw = (
        3.78 * math.log(bili)
        + 11.2 * math.log(inr_used)
        + 9.57 * math.log(creat_used)
        + 6.43
    )
    score = max(6, min(int(round(raw)), 40))

    return {
        "meld_score": score,
        "meld_raw": round(raw, 2),
        "formula": "legacy MELD (2001)",
        "allocation_use": False,
        "components_used": {
            "bilirubin_mg_dl": bili,
            "inr": inr_used,
            "creatinine_mg_dl": creat_used,
            "dialysis": bool(dialysis),
        },
    }


def calculate_child_pugh(
    bilirubin: float,
    albumin: float,
    inr: float,
    ascites: str,
    encephalopathy: str,
    creatinine: Optional[float] = None,
    dialysis: bool = False,
) -> Dict[str, Any]:
    """Calculate the conventional five-component Child-Pugh score and class."""
    bilirubin = _finite_number("Bilirubin", bilirubin, allow_zero=True)
    albumin = _finite_number("Albumin", albumin, allow_zero=False)
    inr = _finite_number("INR", inr, allow_zero=False)
    if creatinine is not None:
        creatinine = _finite_number("Creatinine", creatinine, allow_zero=False)

    scores = {
        "bilirubin": _score_bilirubin(bilirubin),
        "albumin": _score_albumin(albumin),
        "inr": _score_inr(inr),
        "ascites": _score_ascites(ascites),
        "encephalopathy": _score_encephalopathy(encephalopathy),
    }
    total = sum(scores.values())
    child_class = _child_pugh_class(total)

    result: Dict[str, Any] = {
        "tool": "child-pugh-turcotte-calculator",
        "child_pugh_score": total,
        "child_pugh_class": child_class,
        "class_description": _class_description(child_class),
        "one_year_survival_pct": _one_year_survival(child_class),
        "survival_note": "Legacy class-level estimate; not an individualized prognosis.",
        "component_scores": {
            "bilirubin": {"value_mg_dl": bilirubin, "points": scores["bilirubin"]},
            "albumin": {"value_g_dl": albumin, "points": scores["albumin"]},
            "inr": {"value": inr, "points": scores["inr"]},
            "ascites": {"value": ascites, "points": scores["ascites"]},
            "encephalopathy": {"value": encephalopathy, "points": scores["encephalopathy"]},
        },
        "classification": f"Child-Pugh {child_class} ({total}/15)",
        "interpretation": "Reference calculation only; clinical decisions require full patient context.",
    }

    if creatinine is not None:
        result["meld"] = calculate_meld(bilirubin, inr, creatinine, dialysis=dialysis)
    elif dialysis:
        raise ValueError("Creatinine is required when dialysis is specified")

    return result


def process_batch(input_csv: str, output_csv: str) -> int:
    """Score rows from a CSV and write results plus a per-row error field."""
    input_path = Path(input_csv)
    output_path = Path(output_csv)
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        required = {"bilirubin", "albumin", "inr"}
        missing = sorted(required.difference(fieldnames))
        if missing:
            raise ValueError(f"Missing required CSV column(s): {', '.join(missing)}")
        rows = list(reader)

    added_fields = [
        "child_pugh_score",
        "child_pugh_class",
        "class_description",
        "one_year_survival_pct",
        "legacy_meld_score",
        "error",
    ]
    out_fields = fieldnames + [name for name in added_fields if name not in fieldnames]
    out_rows = []

    for source in rows:
        row = dict(source)
        try:
            creat_text = (row.get("creatinine") or "").strip()
            dialysis_text = (row.get("dialysis") or "").strip().lower()
            dialysis = dialysis_text in {"1", "true", "yes", "y"}
            result = calculate_child_pugh(
                bilirubin=float(row["bilirubin"]),
                albumin=float(row["albumin"]),
                inr=float(row["inr"]),
                ascites=row.get("ascites") or "none",
                encephalopathy=row.get("encephalopathy") or "none",
                creatinine=float(creat_text) if creat_text else None,
                dialysis=dialysis,
            )
            row.update(
                child_pugh_score=result["child_pugh_score"],
                child_pugh_class=result["child_pugh_class"],
                class_description=result["class_description"],
                one_year_survival_pct=result["one_year_survival_pct"],
                legacy_meld_score=result.get("meld", {}).get("meld_score", ""),
                error="",
            )
        except (TypeError, ValueError, KeyError) as exc:
            row.update(
                child_pugh_score="",
                child_pugh_class="",
                class_description="",
                one_year_survival_pct="",
                legacy_meld_score="",
                error=str(exc),
            )
        out_rows.append(row)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=out_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out_rows)

    return len(out_rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Child-Pugh-Turcotte score calculator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    single = subparsers.add_parser("single", help="Evaluate one set of values")
    single.add_argument("--bilirubin", type=float, required=True, help="Total bilirubin (mg/dL)")
    single.add_argument("--albumin", type=float, required=True, help="Albumin (g/dL)")
    single.add_argument("--inr", type=float, required=True, help="International Normalized Ratio")
    single.add_argument("--ascites", choices=["none", "mild/controlled", "moderate-severe"], default="none")
    single.add_argument("--encephalopathy", choices=["none", "grade I-II", "grade III-IV"], default="none")
    single.add_argument("--creatinine", type=float, help="Creatinine (mg/dL) for legacy MELD")
    single.add_argument("--dialysis", action="store_true", help="Use creatinine 4.0 mg/dL in legacy MELD")

    batch = subparsers.add_parser("batch", help="Process a CSV file")
    batch.add_argument("-i", "--input", required=True, help="Input CSV path")
    batch.add_argument("-o", "--output", default="results.csv", help="Output CSV path")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "single":
            result = calculate_child_pugh(
                args.bilirubin,
                args.albumin,
                args.inr,
                args.ascites,
                args.encephalopathy,
                args.creatinine,
                args.dialysis,
            )
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            count = process_batch(args.input, args.output)
            print(f"Processed {count} record(s) -> {args.output}")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
