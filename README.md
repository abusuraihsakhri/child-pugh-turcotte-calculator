# Child-Pugh-Turcotte (CPT) Score & MELD Liver Disease Calculator

> **Domain:** Hepatology, Gastroenterology & Liver Transplantation  
> **Clinical Guidelines & Standards:** Child & Turcotte (Surgery 1964), Pugh et al. (Br J Surg 1973), AASLD Cirrhosis & Portal Hypertension Guidelines, EASL Clinical Practice Guidelines, Kamath et al. (Hepatology 2001, MELD formula)

---

## 📖 Clinical Overview

The **Child-Pugh-Turcotte (CPT) Calculator** stratifies chronic liver disease severity and cirrhosis prognosis. It evaluates five objective biochemical and subjective physical parameters (Total Bilirubin, Serum Albumin, International Normalized Ratio / Prothrombin Time, Ascites, and Hepatic Encephalopathy) to classify disease into Class A, B, or C, predicting 1-year and 2-year perioperative and overall survival. Additionally, it computes the Model for End-Stage Liver Disease (MELD) score when Serum Creatinine is available.

### Child-Pugh Scoring System

| Clinical / Laboratory Parameter | 1 Point | 2 Points | 3 Points |
|:---|:---:|:---:|:---:|
| **Total Bilirubin (mg/dL)** | $< 2.0$ | $2.0 - 3.0$ | $> 3.0$ |
| *(In PBC / PSC / Cholestatic)* | $< 4.0$ | $4.0 - 10.0$ | $> 10.0$ |
| **Serum Albumin (g/dL)** | $> 3.5$ | $2.8 - 3.5$ | $< 2.8$ |
| **INR (Prothrombin Time prolongation)** | $< 1.7$ ($< 4\text{s}$) | $1.7 - 2.3$ ($4 - 6\text{s}$) | $> 2.3$ ($> 6\text{s}$) |
| **Ascites** | None | Mild / Diuretic-controlled | Moderate to Severe / Refractory |
| **Hepatic Encephalopathy** | None | Grade I – II | Grade III – IV |

### Classification & Survival

| Child-Pugh Class | Point Total | 1-Year Actuarial Survival | 2-Year Actuarial Survival | Perioperative Mortality (Abdominal Surgery) |
|:---:|:---:|:---:|:---:|:---:|
| **Class A** | 5 – 6 | 100% | 85% | ~10% |
| **Class B** | 7 – 9 | 80% | 60% | ~30% |
| **Class C** | 10 – 15 | 45% | 35% | ~70% – 80% |

---

## 💻 CLI Quickstart & Usage

### 1. Evaluate Individual Patient
```bash
python cli.py single --bilirubin 2.5 --albumin 3.0 --inr 1.9 --ascites mild/controlled --encephalopathy "grade I-II" --creatinine 1.5
```

### 2. Batch Process Cirrhosis Patient CSV Dataset
```bash
python cli.py batch -i sample.csv -o out_results.csv
```

---

## 🧪 Verification & Testing

Execute comprehensive unit tests via pytest:
```bash
python -m pytest -p no:zarr
```
