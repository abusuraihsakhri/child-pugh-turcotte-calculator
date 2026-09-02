# Child Pugh Turcotte Calculator

> **Domain:** Gastroenterology, Hepatology & Clinical Nutrition  
> **Reference Guidelines & Standards:** `AASLD & ACG Clinical Practice Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

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

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_meld()`**: Calculate MELD (Model for End-Stage Liver Disease) score.

MELD = 3.78 * ln(bilirubin) + 11.2 * ln(INR) + 9.57 * ln(creatinine) + 6.43

Values are floored at 1.0 per MELD convention. Final score capped at 40.
- **`calculate_child_pugh()`**: Calculate Child-Pugh-Turcotte score and classification.

Parameters:
    bilirubin: Serum bilirubin in mg/dL
    albumin: Serum albumin in g/dL
    inr: International Normalized Ratio
    ascites: 'none', 'mild/controlled', or 'moderate-severe'
    encephalopathy: 'none', 'grade I-II', or 'grade III-IV'
    creatinine: Serum creatinine in mg/dL (optional, for MELD calculation)

Returns:
    Dict with scores, class, survival estimates, and MELD comparison.
- **`process_batch()`**: Process a CSV of patients and write scored results.
- **`main()`** — calculates and validates main parameters.

---

## 📐 Mathematical Formulation & Logic

```text
  Calculates the Child-Pugh score (5-15) and classification (A, B, C) for
  MELD formula:
  Calculate MELD (Model for End-Stage Liver Disease) score.
  Calculate Child-Pugh-Turcotte score and classification.
  meld = calculate_meld(bilirubin, inr, creatinine)
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --input data.csv
```

### Parameter Reference
- `--interactive`: Launch guided terminal interactive wizard.
- `--input <path>`: Evaluate input from JSON or CSV specification.
- `--json`: Output deterministic structured results in JSON format.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Parameter / observation metric | Required |
| `v1` | Parameter / observation metric | Required |
| `v2` | Parameter / observation metric | Required |
| `v3` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t child-pugh-turcotte-calculator .
docker run -p 8000:8000 child-pugh-turcotte-calculator
```
