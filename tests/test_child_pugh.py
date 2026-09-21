import csv
import math

import pytest

from child_pugh import (
    _child_pugh_class,
    _score_albumin,
    _score_ascites,
    _score_bilirubin,
    _score_encephalopathy,
    _score_inr,
    calculate_child_pugh,
    calculate_meld,
    process_batch,
)


def test_component_boundaries():
    assert [_score_bilirubin(x) for x in (1.99, 2.0, 3.0, 3.01)] == [1, 2, 2, 3]
    assert [_score_albumin(x) for x in (3.51, 3.5, 2.8, 2.79)] == [1, 2, 2, 3]
    assert [_score_inr(x) for x in (1.69, 1.7, 2.3, 2.31)] == [1, 2, 2, 3]
    assert _score_ascites("mild/controlled") == 2
    assert _score_encephalopathy("grade III-IV") == 3


@pytest.mark.parametrize("score, expected", [(5, "A"), (6, "A"), (7, "B"), (9, "B"), (10, "C"), (15, "C")])
def test_class_boundaries(score, expected):
    assert _child_pugh_class(score) == expected


def test_full_calculation_classes():
    low = calculate_child_pugh(1.0, 4.0, 1.2, "none", "none")
    high = calculate_child_pugh(5.0, 2.0, 3.0, "moderate-severe", "grade III-IV")
    assert (low["child_pugh_score"], low["child_pugh_class"]) == (5, "A")
    assert (high["child_pugh_score"], high["child_pugh_class"]) == (15, "C")
    assert "recommend" not in " ".join(high.keys()).lower()


def test_invalid_numeric_values_rejected():
    for value in (math.nan, math.inf, -1):
        with pytest.raises(ValueError):
            calculate_child_pugh(value, 4.0, 1.2, "none", "none")
    with pytest.raises(ValueError):
        calculate_child_pugh(1.0, 4.0, 0, "none", "none")


def test_invalid_categories_rejected():
    with pytest.raises(ValueError):
        calculate_child_pugh(1, 4, 1.2, "unknown", "none")
    with pytest.raises(ValueError):
        calculate_child_pugh(1, 4, 1.2, "none", "unknown")


def test_legacy_meld_floor_ceiling_and_dialysis_rule():
    assert calculate_meld(1, 1, 1)["meld_score"] == 6
    capped = calculate_meld(4, 2.5, 20)
    at_four = calculate_meld(4, 2.5, 4)
    assert capped["meld_score"] == at_four["meld_score"]
    assert capped["components_used"]["creatinine_mg_dl"] == 4.0
    assert calculate_meld(2, 1.5, 1, dialysis=True)["components_used"]["creatinine_mg_dl"] == 4.0


def test_batch_outputs_errors_without_mixing_types(tmp_path):
    source = tmp_path / "input.csv"
    target = tmp_path / "output.csv"
    source.write_text(
        "patient_id,bilirubin,albumin,inr,ascites,encephalopathy,creatinine\n"
        "A,1.5,4.0,1.2,none,none,1.0\n"
        "B,not-a-number,3.0,1.9,mild/controlled,grade I-II,1.5\n",
        encoding="utf-8",
    )
    assert process_batch(str(source), str(target)) == 2
    rows = list(csv.DictReader(target.open(encoding="utf-8")))
    assert rows[0]["child_pugh_class"] == "A"
    assert rows[0]["legacy_meld_score"]
    assert rows[0]["error"] == ""
    assert rows[1]["child_pugh_score"] == ""
    assert rows[1]["error"]


def test_batch_requires_core_columns(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text("bilirubin,albumin\n1.0,4.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required CSV"):
        process_batch(str(source), str(tmp_path / "out.csv"))
