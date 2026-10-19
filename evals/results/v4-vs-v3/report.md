# Evaluation results

Selected skill: v4. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.

## development

| Metric | v3 | v4 | Difference [95% interval] |
|---|---:|---:|---:|
| all | 97.8% | 98.6% | +0.81 [-1.08, +2.94] pp |
| fidelity | 98.9% | 99.4% | +0.56 [-1.54, +2.17] pp |
| style | 95.5% | 97.3% | +1.82 [-4.17, +7.50] pp |
| argument | 96.7% | 96.7% | +0.00 [+0.00, +0.00] pp |
| proof | 100.0% | 100.0% | +0.00 [+0.00, +0.00] pp |
| holistic | 4.64 | 4.75 | +0.11 [+0.01, +0.21] |
| words | 42 | 50 | — |

| Configuration | v3 assertions / holistic | v4 assertions / holistic |
|---|---:|---:|
| astra-high | 100.0% / 4.75 | 100.0% / 4.88 |
| astra-medium | 100.0% / 4.88 | 100.0% / 4.75 |
| fable | 97.3% / 4.50 | 100.0% / 4.88 |
| haiku | 89.2% / 4.12 | 91.9% / 4.50 |
| luna-medium | 94.6% / 4.12 | 97.3% / 4.50 |
| opus-low | 100.0% / 4.62 | 100.0% / 5.00 |
| opus-xhigh | 100.0% / 4.88 | 100.0% / 4.88 |
| sol-low | 100.0% / 4.88 | 100.0% / 4.88 |
| sonnet-high | 97.3% / 4.75 | 97.3% / 4.75 |
| sonnet-low | 100.0% / 4.88 | 100.0% / 4.50 |

## heldout2

| Metric | v3 | v4 | Difference [95% interval] |
|---|---:|---:|---:|
| all | 98.8% | 98.5% | -0.24 [-1.58, +0.89] pp |
| fidelity | 97.8% | 97.8% | +0.00 [-2.11, +2.35] pp |
| style | 100.0% | 100.0% | +0.00 [+0.00, +0.00] pp |
| argument | 100.0% | 98.8% | -1.25 [-5.00, +0.00] pp |
| proof | 98.0% | 98.0% | +0.00 [-5.00, +3.33] pp |
| holistic | 4.74 | 4.72 | -0.01 [-0.14, +0.09] |
| words | 142 | 138 | — |

| Configuration | v3 assertions / holistic | v4 assertions / holistic |
|---|---:|---:|
| astra-high | 100.0% / 4.75 | 100.0% / 4.75 |
| astra-medium | 100.0% / 4.62 | 100.0% / 4.75 |
| fable | 97.6% / 4.88 | 97.6% / 5.00 |
| haiku | 95.1% / 4.12 | 100.0% / 4.75 |
| luna-medium | 95.1% / 4.38 | 90.2% / 4.00 |
| opus-low | 100.0% / 4.88 | 100.0% / 4.62 |
| opus-xhigh | 100.0% / 5.00 | 97.6% / 4.88 |
| sol-low | 100.0% / 4.88 | 100.0% / 4.88 |
| sonnet-high | 100.0% / 4.88 | 100.0% / 4.75 |
| sonnet-low | 100.0% / 5.00 | 100.0% / 4.88 |
