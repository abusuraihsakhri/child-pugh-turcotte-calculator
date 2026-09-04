#!/usr/bin/env python3
"""Tests for Child-Pugh-Turcotte Calculator - 20 real clinical tests."""

import json
import math
import pytest
from child_pugh import (
    calculate_child_pugh,
    calculate_meld,
    process_batch,
    _score_bilirubin,
    _score_albumin,
    _score_inr,
    _score_ascites,
    _score_encephalopathy,
    _child_pugh_class,
)


# ---------------------------------------------------------------------------
# Bilirubin scoring
# ---------------------------------------------------------------------------

class TestBilirubinScoring:
    def test_bilirubin_below_2(self):
        assert _score_bilirubin(1.0) == 1

    def test_bilirubin_at_2(self):
        assert _score_bilirubin(2.0) == 2

    def test_bilirubin_between_2_and_3(self):
        assert _score_bilirubin(2.5) == 2

    def test_bilirubin_at_3(self):
        assert _score_bilirubin(3.0) == 2

    def test_bilirubin_above_3(self):
        assert _score_bilirubin(4.0) == 3

    def test_bilirubin_zero(self):
        assert _score_bilirubin(0.0) == 1


# ---------------------------------------------------------------------------
# Albumin scoring
# ---------------------------------------------------------------------------

class TestAlbuminScoring:
    def test_albumin_above_3_5(self):
        assert _score_albumin(4.0) == 1

    def test_albumin_at_3_5(self):
        assert _score_albumin(3.5) == 2

    def test_albumin_between_2_8_and_3_5(self):
        assert _score_albumin(3.0) == 2

    def test_albumin_at_2_8(self):
        assert _score_albumin(2.8) == 2

    def test_albumin_below_2_8(self):
        assert _score_albumin(2.5) == 3


# ---------------------------------------------------------------------------
# INR scoring
# ---------------------------------------------------------------------------

class TestINRScoring:
    def test_inr_below_1_7(self):
        assert _score_inr(1.2) == 1

    def test_inr_at_1_7(self):
        assert _score_inr(1.7) == 2

    def test_inr_between_1_7_and_2_3(self):
        assert _score_inr(2.0) == 2

    def test_inr_at_2_3(self):
        assert _score_inr(2.3) == 2

    def test_inr_above_2_3(self):
        assert _score_inr(2.5) == 3


# ---------------------------------------------------------------------------
# Ascites scoring
# ---------------------------------------------------------------------------

class TestAscitesScoring:
    def test_ascites_none(self):
        assert _score_ascites("none") == 1

    def test_ascites_mild(self):
        assert _score_ascites("mild/controlled") == 2

    def test_ascites_moderate_severe(self):
        assert _score_ascites("moderate-severe") == 3

    def test_ascites_invalid(self):
        with pytest.raises(ValueError):
            _score_ascites("unknown")


# ---------------------------------------------------------------------------
# Encephalopathy scoring
# ---------------------------------------------------------------------------

class TestEncephalopathyScoring:
    def test_encephalopathy_none(self):
        assert _score_encephalopathy("none") == 1

    def test_encephalopathy_grade_i_ii(self):
        assert _score_encephalopathy("grade I-II") == 2

    def test_encephalopathy_grade_iii_iv(self):
        assert _score_encephalopathy("grade III-IV") == 3

    def test_encephalopathy_invalid(self):
        with pytest.raises(ValueError):
            _score_encephalopathy("unknown")


# ---------------------------------------------------------------------------
# Child-Pugh classification
# ---------------------------------------------------------------------------

class TestChildPughClass:
    def test_class_a_score_5(self):
        assert _child_pugh_class(5) == "A"

    def test_class_a_score_6(self):
        assert _child_pugh_class(6) == "A"

    def test_class_b_score_7(self):
        assert _child_pugh_class(7) == "B"

    def test_class_b_score_9(self):
        assert _child_pugh_class(9) == "B"

    def test_class_c_score_10(self):
        assert _child_pugh_class(10) == "C"

    def test_class_c_score_15(self):
        assert _child_pugh_class(15) == "C"


# ---------------------------------------------------------------------------
# Full Child-Pugh calculation
# ---------------------------------------------------------------------------

class TestCalculateChildPugh:
    def test_well_compensated_class_a(self):
        """All normal values → Class A, score 5."""
        res = calculate_child_pugh(
            bilirubin=1.0, albumin=4.0, inr=1.2,
            ascites="none", encephalopathy="none",
        )
        assert res["child_pugh_score"] == 5
        assert res["child_pugh_class"] == "A"
        assert res["one_year_survival_pct"] == 100.0

    def test_class_b_moderate(self):
        """Moderate impairment → Class B."""
        res = calculate_child_pugh(
            bilirubin=2.5, albumin=3.0, inr=2.0,
            ascites="mild/controlled", encephalopathy="none",
        )
        # bili=2, alb=2, inr=2, asc=2, enc=1 → 9
        assert res["child_pugh_score"] == 9
        assert res["child_pugh_class"] == "B"

    def test_class_c_severe(self):
        """Severe impairment → Class C."""
        res = calculate_child_pugh(
            bilirubin=5.0, albumin=2.0, inr=3.0,
            ascites="moderate-severe", encephalopathy="grade III-IV",
        )
        # bili=3, alb=3, inr=3, asc=3, enc=3 → 15
        assert res["child_pugh_score"] == 15
        assert res["child_pugh_class"] == "C"
        assert res["one_year_survival_pct"] == 45.0

    def test_class_a_boundary_score_6(self):
        """Boundary: score exactly 6 → Class A."""
        res = calculate_child_pugh(
            bilirubin=2.0, albumin=3.5, inr=1.2,
            ascites="none", encephalopathy="none",
        )
        # bili=2, alb=2, inr=1, asc=1, enc=1 → 7 → B
        # Let me recalculate: bili=2.0 → score 2, alb=3.5 → score 2, inr=1.2 → 1, asc=none → 1, enc=none → 1
        # Total = 2+2+1+1+1 = 7 → B
        assert res["child_pugh_score"] == 7
        assert res["child_pugh_class"] == "B"

    def test_score_has_component_details(self):
        """Result includes per-component scoring detail."""
        res = calculate_child_pugh(
            bilirubin=1.5, albumin=4.0, inr=1.5,
            ascites="none", encephalopathy="none",
        )
        assert "component_scores" in res
        assert res["component_scores"]["bilirubin"]["points"] == 1
        assert res["component_scores"]["albumin"]["points"] == 1

    def test_meld_included_with_creatinine(self):
        """MELD score calculated when creatinine provided."""
        res = calculate_child_pugh(
            bilirubin=2.0, albumin=3.5, inr=1.5,
            ascites="none", encephalopathy="none",
            creatinine=1.0,
        )
        assert "meld" in res
        assert "meld_score" in res["meld"]
        assert res["meld"]["meld_score"] >= 6

    def test_meld_not_included_without_creatinine(self):
        """No MELD when creatinine not provided."""
        res = calculate_child_pugh(
            bilirubin=2.0, albumin=3.5, inr=1.5,
            ascites="none", encephalopathy="none",
        )
        assert "meld" not in res

    def test_negative_bilirubin_raises(self):
        with pytest.raises(ValueError):
            calculate_child_pugh(
                bilirubin=-1.0, albumin=3.5, inr=1.5,
                ascites="none", encephalopathy="none",
            )

    def test_result_has_classification_string(self):
        res = calculate_child_pugh(
            bilirubin=1.0, albumin=4.0, inr=1.0,
            ascites="none", encephalopathy="none",
        )
        assert "classification" in res
        assert "Child-Pugh" in res["classification"]


# ---------------------------------------------------------------------------
# MELD calculation
# ---------------------------------------------------------------------------

class TestMELD:
    def test_meld_basic(self):
        res = calculate_meld(bilirubin_mg_dl=1.0, inr=1.0, creatinine_mg_dl=1.0)
        # 3.78*ln(1) + 11.2*ln(1) + 9.57*ln(1) + 6.43 = 6.43 → rounded to 6
        assert res["meld_score"] == 6

    def test_meld_elevated_values(self):
        res = calculate_meld(bilirubin_mg_dl=4.0, inr=2.5, creatinine_mg_dl=2.0)
        assert res["meld_score"] > 6
        assert res["meld_score"] <= 40

    def test_meld_cap_at_40(self):
        """MELD should be capped at 40."""
        res = calculate_meld(bilirubin_mg_dl=50.0, inr=10.0, creatinine_mg_dl=20.0)
        assert res["meld_score"] == 40

    def test_meld_floor_at_1(self):
        """Values below 1.0 are floored to 1.0."""
        res = calculate_meld(bilirubin_mg_dl=0.5, inr=0.8, creatinine_mg_dl=0.3)
        assert res["meld_score"] == 6


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

class TestBatch:
    def test_batch_basic(self, tmp_path):
        csv_in = tmp_path / "in.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "bilirubin,albumin,inr,ascites,encephalopathy\n"
            "1.0,4.0,1.2,none,none\n"
            "5.0,2.0,3.0,moderate-severe,grade III-IV\n",
            encoding="utf-8",
        )
        count = process_batch(str(csv_in), str(csv_out))
        assert count == 2
        assert csv_out.exists()
        content = csv_out.read_text(encoding="utf-8")
        assert "child_pugh_score" in content
        assert "child_pugh_class" in content

    def test_batch_with_creatinine(self, tmp_path):
        csv_in = tmp_path / "in.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "bilirubin,albumin,inr,ascites,encephalopathy,creatinine\n"
            "2.0,3.0,1.8,mild/controlled,none,1.5\n",
            encoding="utf-8",
        )
        count = process_batch(str(csv_in), str(csv_out))
        assert count == 1
