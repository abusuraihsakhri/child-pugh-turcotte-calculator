# Child-Pugh-Turcotte Calculator

A compact reference calculator for the conventional Child-Pugh-Turcotte score used to classify chronic liver disease severity. The repository also provides a command-line interface and CSV batch processing.

## Features

- Calculates the five-component Child-Pugh score (5–15) and class (A, B, or C).
- Shows each component's point contribution.
- Optionally calculates the legacy 2001 MELD formula for comparison, including the conventional 4.0 mg/dL creatinine ceiling and dialysis rule.
- Processes CSV files with per-row validation errors rather than failing an entire batch.
- Provides a static browser interface with light/dark themes and no server-side data processing.

Clinical scope: this is a reference implementation, not a diagnostic or treatment system. The optional MELD output is the historical 2001 formula and is not the current OPTN liver-allocation MELD. Current OPTN MELD calculations use additional variables and policy-specific rules; use the official OPTN calculator for allocation decisions.

## Child-Pugh scoring

| Component | 1 point | 2 points | 3 points |
| --- | --- | --- | --- |
| Bilirubin (mg/dL) | <2.0 | 2.0–3.0 | >3.0 |
| Albumin (g/dL) | >3.5 | 2.8–3.5 | <2.8 |
| INR | <1.7 | 1.7–2.3 | >2.3 |
| Ascites | None | Mild / controlled | Moderate / severe |
| Encephalopathy | None | Grade I–II | Grade III–IV |

Class A = 5–6 points, Class B = 7–9, and Class C = 10–15.

## CLI

Single calculation:

    python cli.py single --bilirubin 2.5 --albumin 3.0 --inr 1.9 --ascites mild/controlled --encephalopathy "grade I-II" --creatinine 1.5

Batch processing:

    python cli.py batch -i sample.csv -o results.csv

Required CSV columns are bilirubin, albumin, and inr. Ascites, encephalopathy, creatinine, and dialysis are optional.

## Testing

    python -m pip install pytest==9.0.2
    python -m pytest
    python -m compileall -q child_pugh.py cli.py tests
    node --test tests/web.test.mjs

The runtime calculator has no third-party Python dependencies.

## Privacy and browser support

The GitHub Pages application performs calculations entirely in the browser. It does not upload clinical values or store them; only the selected light/dark theme is retained in browser storage. Current desktop and mobile versions of Chrome, Edge, Firefox, and Safari are supported.

## Technology

Python 3.10+ for CLI/batch use; HTML, CSS, and JavaScript for the static browser application; GitHub Actions for CI and Pages deployment.

## License

MIT. See LICENSE.
