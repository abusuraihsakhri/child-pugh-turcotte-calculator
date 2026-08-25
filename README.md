# Child-Pugh-Turcotte (CPT) Score Calculator

Real implementation of the Child-Pugh-Turcotte scoring system for liver disease severity assessment in cirrhosis patients.

## What It Does

Calculates the **Child-Pugh score (5-15)** and **classification (A, B, C)** based on five clinical parameters:

| Parameter | 1 point | 2 points | 3 points |
|-----------|---------|----------|----------|
| Bilirubin (mg/dL) | <2 | 2-3 | >3 |
| Albumin (g/dL) | >3.5 | 2.8-3.5 | <2.8 |
| INR | <1.7 | 1.7-2.3 | >2.3 |
| Ascites | None | Mild/controlled | Moderate-severe |
| Encephalopathy | None | Grade I-II | Grade III-IV |

**Classification:**
- **Class A (5-6):** Well-compensated — ~100% 1-year survival
- **Class B (7-9):** Significant compromise — ~80% 1-year survival
- **Class C (10-15):** Decompensated — ~45% 1-year survival

Also calculates **MELD score** when creatinine is provided for transplant prioritization comparison.

## Installation

Zero dependencies — Python 3.7+ stdlib only.

## Usage

### Single Patient

```bash
python child_pugh.py single \
  --bilirubin 2.5 \
  --albumin 3.0 \
  --inr 2.0 \
  --ascites "mild/controlled" \
  --encephalopathy "none" \
  --creatinine 1.2
```

### Batch Processing

```bash
python child_pugh.py batch -i patients.csv -o results.csv
```

CSV columns: `bilirubin`, `albumin`, `inr`, `ascites`, `encephalopathy`, `creatinine` (optional)

### Python API

```python
from child_pugh import calculate_child_pugh, calculate_meld

result = calculate_child_pugh(
    bilirubin=2.5, albumin=3.0, inr=2.0,
    ascites="mild/controlled", encephalopathy="none",
    creatinine=1.2,
)
print(result["child_pugh_score"])   # 9
print(result["child_pugh_class"])   # "B"
print(result["meld"]["meld_score"]) # MELD score
```

## Running Tests

```bash
python -m pytest test_child_pugh.py -v
```

## Clinical Reference

Child CG, Turcotte JG. Surgery and portal hypertension. In: The Liver and Portal Hypertension. Saunders, 1964.

Pugh RN et al. Transection of the oesophagus for bleeding oesophageal varices. Br J Surg. 1973;60(8):646-9.

## License

MIT
