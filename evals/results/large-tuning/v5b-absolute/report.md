# Evaluation results

Selected skill: v5b. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.

## development

| Metric | v4 | v5b | Difference [95% interval] |
|---|---:|---:|---:|
| all | 97.9% | 98.4% | +0.58 [-0.39, +1.74] pp |
| fidelity | 99.3% | 99.3% | +0.00 [-1.49, +1.49] pp |
| style | 93.0% | 95.0% | +2.00 [+0.00, +6.82] pp |
| argument | 98.9% | 98.9% | +0.00 [+0.00, +0.00] pp |
| proof | 98.3% | 100.0% | +1.67 [+0.00, +6.25] pp |
| holistic | 4.45 | 4.47 | +0.02 [-0.16, +0.24] |
| words | 312 | 322 | — |

| Configuration | v4 assertions / holistic | v5b assertions / holistic |
|---|---:|---:|
| astra-medium | 98.4% / 4.65 | 100.0% / 4.70 |
| haiku | 96.9% / 4.30 | 96.9% / 4.15 |
| luna-medium | 96.9% / 4.15 | 97.7% / 4.35 |
| sonnet-high | 99.2% / 4.70 | 99.2% / 4.70 |
