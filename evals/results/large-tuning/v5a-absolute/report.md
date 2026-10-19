# Evaluation results

Selected skill: v5a. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.

## development

| Metric | v4 | v5a | Difference [95% interval] |
|---|---:|---:|---:|
| all | 98.8% | 98.6% | -0.19 [-1.32, +0.76] pp |
| fidelity | 99.3% | 99.6% | +0.37 [+0.00, +1.14] pp |
| style | 97.0% | 96.0% | -1.00 [-3.41, +0.00] pp |
| argument | 100.0% | 100.0% | +0.00 [+0.00, +0.00] pp |
| proof | 98.3% | 96.7% | -1.67 [-12.50, +6.25] pp |
| holistic | 4.38 | 4.49 | +0.11 [-0.04, +0.26] |
| words | 312 | 317 | — |

| Configuration | v4 assertions / holistic | v5a assertions / holistic |
|---|---:|---:|
| astra-medium | 99.2% / 4.65 | 100.0% / 4.75 |
| haiku | 99.2% / 4.20 | 99.2% / 4.40 |
| luna-medium | 97.7% / 4.05 | 95.3% / 4.05 |
| sonnet-high | 99.2% / 4.60 | 100.0% / 4.75 |
