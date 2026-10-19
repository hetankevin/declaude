# Evaluation results

Selected skill: v5a. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.

## development

| Metric | v4 | v5a | Difference [95% interval] |
|---|---:|---:|---:|
| all | 97.0% | 96.4% | -0.57 [-2.10, +0.75] pp |
| fidelity | 98.5% | 98.5% | +0.00 [-1.12, +1.14] pp |
| style | 92.6% | 90.7% | -1.85 [-6.90, +3.00] pp |
| argument | 97.8% | 96.7% | -1.09 [-5.00, +2.63] pp |
| proof | 96.9% | 96.9% | +0.00 [+0.00, +0.00] pp |
| holistic | 4.44 | 4.36 | -0.08 [-0.20, +0.06] |
| words | 302 | 301 | — |

| Configuration | v4 assertions / holistic | v5a assertions / holistic |
|---|---:|---:|
| astra-medium | 99.2% / 4.85 | 99.2% / 4.75 |
| haiku | 97.0% / 4.45 | 95.5% / 4.15 |
| luna-medium | 93.2% / 3.95 | 91.7% / 3.85 |
| sonnet-high | 98.5% / 4.50 | 99.2% / 4.70 |
