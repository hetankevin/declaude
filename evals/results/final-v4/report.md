# Evaluation results

Selected skill: v4. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.

## development

| Metric | none | v4 | Difference [95% interval] |
|---|---:|---:|---:|
| all | 90.8% | 98.6% | +7.84 [+3.85, +13.51] pp |
| fidelity | 98.9% | 99.4% | +0.56 [-1.54, +2.50] pp |
| style | 74.5% | 97.3% | +22.73 [+7.78, +39.09] pp |
| argument | 96.7% | 96.7% | +0.00 [+0.00, +0.00] pp |
| proof | 94.0% | 100.0% | +6.00 [+0.00, +10.00] pp |
| holistic | 4.36 | 4.75 | +0.39 [+0.15, +0.64] |
| words | 54 | 50 | — |

| Configuration | none assertions / holistic | v4 assertions / holistic |
|---|---:|---:|
| astra-high | 100.0% / 4.88 | 100.0% / 4.88 |
| astra-medium | 97.3% / 4.50 | 100.0% / 4.75 |
| fable | 81.1% / 3.88 | 100.0% / 4.88 |
| haiku | 83.8% / 4.12 | 91.9% / 4.50 |
| luna-medium | 89.2% / 4.38 | 97.3% / 4.50 |
| opus-low | 94.6% / 4.75 | 100.0% / 5.00 |
| opus-xhigh | 94.6% / 4.62 | 100.0% / 4.88 |
| sol-low | 100.0% / 4.62 | 100.0% / 4.88 |
| sonnet-high | 86.5% / 4.12 | 97.3% / 4.75 |
| sonnet-low | 81.1% / 3.75 | 100.0% / 4.50 |

## heldout2

| Metric | none | v4 | Difference [95% interval] |
|---|---:|---:|---:|
| all | 95.9% | 98.5% | +2.68 [+0.48, +4.77] pp |
| fidelity | 93.3% | 97.8% | +4.44 [+0.00, +9.44] pp |
| style | 98.0% | 100.0% | +2.00 [+0.00, +6.67] pp |
| argument | 98.8% | 98.8% | +0.00 [+0.00, +0.00] pp |
| proof | 96.0% | 98.0% | +2.00 [-5.00, +6.67] pp |
| holistic | 4.55 | 4.72 | +0.17 [-0.08, +0.42] |
| words | 152 | 138 | — |

| Configuration | none assertions / holistic | v4 assertions / holistic |
|---|---:|---:|
| astra-high | 97.6% / 4.75 | 100.0% / 4.75 |
| astra-medium | 100.0% / 4.62 | 100.0% / 4.75 |
| fable | 95.1% / 4.75 | 97.6% / 5.00 |
| haiku | 92.7% / 4.00 | 100.0% / 4.75 |
| luna-medium | 85.4% / 3.62 | 90.2% / 4.00 |
| opus-low | 92.7% / 4.50 | 100.0% / 4.62 |
| opus-xhigh | 100.0% / 4.88 | 97.6% / 4.88 |
| sol-low | 100.0% / 4.88 | 100.0% / 4.88 |
| sonnet-high | 97.6% / 4.88 | 100.0% / 4.75 |
| sonnet-low | 97.6% / 4.62 | 100.0% / 4.88 |
