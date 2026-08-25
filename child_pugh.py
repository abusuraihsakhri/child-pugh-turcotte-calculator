#!/usr/bin/env python3
"""
Child-Pugh-Turcotte (CPT) Score for Liver Disease Severity

Calculates the Child-Pugh score (5-15) and classification (A, B, C) for
chronic liver disease / cirrhosis severity assessment. Also computes MELD
score for transplant prioritization comparison.

Parameters:
  - Bilirubin (mg/dL)
  - Albumin (g/dL)
  - INR
  - Ascites (none / mild-controlled / moderate-severe)
  - Encephalopathy (none / grade I-II / grade III-IV)

Scoring:
  Each parameter is scored 1, 2, or 3 points.
  Total 5-15: Class A (5-6), Class B (7-9), Class C (10-15)

MELD formula:
  MELD = 3.78 * ln(bilirubin) + 11.2 * ln(INR) + 9.57 * ln(creatinine) + 6.43

Zero-dependency Python implementation.
License: MIT
"""

import argparse
import csv
import json
import math
import sys
from typing import Dict, Any, Optional


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _score_bilirubin(bilirubin_mg_dl: float) -> int:
    """Bilirubin (mg/dL): <2 → 1, 2-3 → 2, >3 → 3"""
    if bilirubin_mg_dl < 2.0:
        return 1
    elif bilirubin_mg_dl <= 3.0:
        return 2
    else:
        return 3


def _score_albumin(albumin_g_dl: float) -> int:
    """Albumin (g/dL): >3.5 → 1, 2.8-3.5 → 2, <2.8 → 3"""
    if albumin_g_dl > 3.5:
        return 1
    elif albumin_g_dl >= 2.8:
        return 2
    else:
        return 3


def _score_inr(inr: float) -> int:
    """INR: <1.7 → 1, 1.7-2.3 → 2, >2.3 → 3"""
    if inr < 1.7:
        return 1
    elif inr <= 2.3:
        return 2
    else:
        return 3


def _score_ascites(ascites: str) -> int:
    """Ascites: none → 1, mild/controlled → 2, moderate-severe → 3"""
    ascites_lower = ascites.strip().lower().replace("-", " ").replace("_", " ")
    if ascites_lower in ("none", "no", "absent", "0"):
        return 1
    elif ascites_lower in ("mild", "controlled", "mild controlled", "mild/controlled",
                            "slight", "1", "diuretic responsive"):
        return 2
    elif ascites_lower in ("moderate", "severe", "moderate severe", "moderate/severe",
                            "moderate to severe", "refractory", "2", "3"):
        return 3
    else:
        raise ValueError(
            f"Invalid ascites value '{ascites}'. "
            "Use: none, mild/controlled, or moderate-severe"
        )


def _score_encephalopathy(encephalopathy: str) -> int:
    """Encephalopathy: none → 1, grade I-II → 2, grade III-IV → 3"""
    enc_lower = encephalopathy.strip().lower().replace("-", " ").replace("_", " ")
    if enc_lower in ("none", "no", "absent", "0", "grade 0"):
        return 1
    elif enc_lower in ("grade i ii", "grade 1 2", "grade i-ii", "grade 1-2",
                        "i ii", "1 2", "grade i", "grade ii", "grade 1", "grade 2",
                        "minimal", "mild", "moderate"):
        return 2
    elif enc_lower in ("grade iii iv", "grade 3 4", "grade iii-iv", "grade 3-4",
                        "iii iv", "3 4", "grade iii", "grade iv", "grade 3", "grade 4",
                        "severe", "coma"):
        return 3
    else:
        raise ValueError(
            f"Invalid encephalopathy value '{encephalopathy}'. "
            "Use: none, grade I-II, or grade III-IV"
        )


def _child_pugh_class(total_score: int) -> str:
    """Classify total Child-Pugh score."""
    if total_score <= 6:
        return "A"
    elif total_score <= 9:
        return "B"
    else:
        return "C"


def _class_description(cls: str) -> str:
    """Return clinical description for Child-Pugh class."""
    descriptions = {
        "A": "Well-compensated liver disease",
        "B": "Significant functional compromise",
        "C": "Decompensated liver disease",
    }
    return descriptions[cls]


def _one_year_survival(cls: str) -> float:
    """Approximate 1-year survival by Child-Pugh class (%)."""
    return {"A": 100.0, "B": 80.0, "C": 45.0}[cls]


# ---------------------------------------------------------------------------
# MELD score calculation
# ---------------------------------------------------------------------------

def calculate_meld(bilirubin_mg_dl: float, inr: float, creatinine_mg_dl: float) -> Dict[str, Any]:
    """
    Calculate MELD (Model for End-Stage Liver Disease) score.

    MELD = 3.78 * ln(bilirubin) + 11.2 * ln(INR) + 9.57 * ln(creatinine) + 6.43

    Values are floored at 1.0 per MELD convention. Final score capped at 40.
    """
    # Floor at 1.0 per standard MELD rules
    bili = max(bilirubin_mg_dl, 1.0)
    inr_val = max(inr, 1.0)
    creat = max(creatinine_mg_dl, 1.0)

    raw = (3.78 * math.log(bili)
           + 11.2 * math.log(inr_val)
           + 9.57 * math.log(creat)
           + 6.43)

    meld = min(int(round(raw)), 40)
    meld = max(meld, 6)  # minimum MELD is 6

    return {
        "meld_score": meld,
        "meld_raw": round(raw, 2),
        "meld_components": {
            "bilirubin": bilirubin_mg_dl,
            "inr": inr,
            "creatinine": creatinine_mg_dl,
        },
    }


# ---------------------------------------------------------------------------
# Main calculation
# ---------------------------------------------------------------------------

def calculate_child_pugh(
    bilirubin: float,
    albumin: float,
    inr: float,
    ascites: str,
    encephalopathy: str,
    creatinine: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate Child-Pugh-Turcotte score and classification.

    Parameters:
        bilirubin: Serum bilirubin in mg/dL
        albumin: Serum albumin in g/dL
        inr: International Normalized Ratio
        ascites: 'none', 'mild/controlled', or 'moderate-severe'
        encephalopathy: 'none', 'grade I-II', or 'grade III-IV'
        creatinine: Serum creatinine in mg/dL (optional, for MELD calculation)

    Returns:
        Dict with scores, class, survival estimates, and MELD comparison.
    """
    # Validate inputs
    if bilirubin < 0:
        raise ValueError("Bilirubin must be non-negative")
    if albumin < 0:
        raise ValueError("Albumin must be non-negative")
    if inr < 0:
        raise ValueError("INR must be non-negative")

    # Score each component
    s_bili = _score_bilirubin(bilirubin)
    s_alb = _score_albumin(albumin)
    s_inr = _score_inr(inr)
    s_asc = _score_ascites(ascites)
    s_enc = _score_encephalopathy(encephalopathy)

    total = s_bili + s_alb + s_inr + s_asc + s_enc
    child_class = _child_pugh_class(total)

    result = {
        "tool": "child-pugh-turcotte-calculator",
        "child_pugh_score": total,
        "child_pugh_class": child_class,
        "class_description": _class_description(child_class),
        "one_year_survival_pct": _one_year_survival(child_class),
        "component_scores": {
            "bilirubin": {"value_mg_dl": bilirubin, "points": s_bili},
            "albumin": {"value_g_dl": albumin, "points": s_alb},
            "inr": {"value": inr, "points": s_inr},
            "ascites": {"value": ascites, "points": s_asc},
            "encephalopathy": {"value": encephalopathy, "points": s_enc},
        },
        "classification": f"Child-Pugh {child_class} ({total}/15)",
        "clinical_recommendation": _recommendation(child_class, total),
    }

    # Add MELD if creatinine provided
    if creatinine is not None:
        if creatinine < 0:
            raise ValueError("Creatinine must be non-negative")
        meld = calculate_meld(bilirubin, inr, creatinine)
        result["meld"] = meld

    return result


def _recommendation(cls: str, score: int) -> str:
    """Generate clinical recommendation based on Child-Pugh class."""
    if cls == "A":
        return (
            "Well-compensated liver disease. Candidates for surgical resection "
            "and locoregional therapies. Regular surveillance recommended."
        )
    elif cls == "B":
        return (
            "Significant hepatic compromise. Surgical risk increased; consider "
            "transplant evaluation. Locoregional therapies with caution. "
            "Optimize medical management of complications."
        )
    else:
        return (
            "Decompensated liver disease. High surgical mortality. "
            "Transplant evaluation strongly recommended if no contraindications. "
            "Best supportive care if transplant ineligible."
        )


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def process_batch(input_csv: str, output_csv: str) -> int:
    """Process a CSV of patients and write scored results."""
    with open(input_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    out_fields = fieldnames + [
        "child_pugh_score", "child_pugh_class", "class_description",
        "one_year_survival_pct", "clinical_recommendation",
    ]
    out_rows = []
    for r in rows:
        try:
            creat = float(r["creatinine"]) if r.get("creatinine") else None
            res = calculate_child_pugh(
                bilirubin=float(r["bilirubin"]),
                albumin=float(r["albumin"]),
                inr=float(r["inr"]),
                ascites=r.get("ascites", "none"),
                encephalopathy=r.get("encephalopathy", "none"),
                creatinine=creat,
            )
            row_dict = dict(r)
            row_dict["child_pugh_score"] = res["child_pugh_score"]
            row_dict["child_pugh_class"] = res["child_pugh_class"]
            row_dict["class_description"] = res["class_description"]
            row_dict["one_year_survival_pct"] = res["one_year_survival_pct"]
            row_dict["clinical_recommendation"] = res["clinical_recommendation"]
        except (ValueError, KeyError) as e:
            row_dict = dict(r)
            row_dict["child_pugh_score"] = f"ERROR: {e}"
            row_dict["child_pugh_class"] = ""
            row_dict["class_description"] = ""
            row_dict["one_year_survival_pct"] = ""
            row_dict["clinical_recommendation"] = ""
        out_rows.append(row_dict)

    with open(output_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Processed {len(out_rows)} records -> {output_csv}")
    return len(out_rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Child-Pugh-Turcotte (CPT) Score Calculator for Liver Disease Severity"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single evaluation
    sp = subparsers.add_parser("single", help="Evaluate a single patient")
    sp.add_argument("--bilirubin", type=float, required=True,
                    help="Serum bilirubin (mg/dL)")
    sp.add_argument("--albumin", type=float, required=True,
                    help="Serum albumin (g/dL)")
    sp.add_argument("--inr", type=float, required=True,
                    help="International Normalized Ratio")
    sp.add_argument("--ascites", default="none",
                    choices=["none", "mild/controlled", "moderate-severe"],
                    help="Ascites severity (default: none)")
    sp.add_argument("--encephalopathy", default="none",
                    choices=["none", "grade I-II", "grade III-IV"],
                    help="Encephalopathy grade (default: none)")
    sp.add_argument("--creatinine", type=float, default=None,
                    help="Serum creatinine (mg/dL) for MELD calculation")

    # Batch processing
    bp = subparsers.add_parser("batch", help="Batch process CSV file")
    bp.add_argument("-i", "--input", required=True, help="Input CSV file")
    bp.add_argument("-o", "--output", default="results.csv", help="Output CSV file")

    args = parser.parse_args(argv)

    if args.command == "single":
        result = calculate_child_pugh(
            bilirubin=args.bilirubin,
            albumin=args.albumin,
            inr=args.inr,
            ascites=args.ascites,
            encephalopathy=args.encephalopathy,
            creatinine=args.creatinine,
        )
        print(json.dumps(result, indent=2))
    elif args.command == "batch":
        process_batch(args.input, args.output)


if __name__ == "__main__":
    main()
