# Evaluation results

Selected skill: v3. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.

## development

| Metric | none | v3 | Difference [95% interval] |
|---|---:|---:|---:|
| all | 90.8% | 97.8% | +7.03 [+3.61, +11.62] pp |
| fidelity | 98.9% | 98.9% | +0.00 [-1.30, +1.88] pp |
| style | 74.5% | 95.5% | +20.91 [+8.00, +34.00] pp |
| argument | 96.7% | 96.7% | +0.00 [+0.00, +0.00] pp |
| proof | 94.0% | 100.0% | +6.00 [+0.00, +10.00] pp |
| holistic | 4.36 | 4.64 | +0.28 [+0.06, +0.50] |
| words | 54 | 42 | — |

| Configuration | none assertions / holistic | v3 assertions / holistic |
|---|---:|---:|
| astra-high | 100.0% / 4.88 | 100.0% / 4.75 |
| astra-medium | 97.3% / 4.50 | 100.0% / 4.88 |
| fable | 81.1% / 3.88 | 97.3% / 4.50 |
| haiku | 83.8% / 4.12 | 89.2% / 4.12 |
| luna-medium | 89.2% / 4.38 | 94.6% / 4.12 |
| opus-low | 94.6% / 4.75 | 100.0% / 4.62 |
| opus-xhigh | 94.6% / 4.62 | 100.0% / 4.88 |
| sol-low | 100.0% / 4.62 | 100.0% / 4.88 |
| sonnet-high | 86.5% / 4.12 | 97.3% / 4.75 |
| sonnet-low | 81.1% / 3.75 | 100.0% / 4.88 |

## heldout2

| Metric | none | v3 | Difference [95% interval] |
|---|---:|---:|---:|
| all | 95.9% | 98.8% | +2.93 [+1.19, +4.63] pp |
| fidelity | 93.3% | 97.8% | +4.44 [+1.18, +8.18] pp |
| style | 98.0% | 100.0% | +2.00 [+0.00, +6.67] pp |
| argument | 98.8% | 100.0% | +1.25 [+0.00, +5.00] pp |
| proof | 96.0% | 98.0% | +2.00 [+0.00, +3.33] pp |
| holistic | 4.55 | 4.74 | +0.19 [-0.01, +0.39] |
| words | 152 | 142 | — |

| Configuration | none assertions / holistic | v3 assertions / holistic |
|---|---:|---:|
| astra-high | 97.6% / 4.75 | 100.0% / 4.75 |
| astra-medium | 100.0% / 4.62 | 100.0% / 4.62 |
| fable | 95.1% / 4.75 | 97.6% / 4.88 |
| haiku | 92.7% / 4.00 | 95.1% / 4.12 |
| luna-medium | 85.4% / 3.62 | 95.1% / 4.38 |
| opus-low | 92.7% / 4.50 | 100.0% / 4.88 |
| opus-xhigh | 100.0% / 4.88 | 100.0% / 5.00 |
| sol-low | 100.0% / 4.88 | 100.0% / 4.88 |
| sonnet-high | 97.6% / 4.88 | 100.0% / 4.88 |
| sonnet-low | 97.6% / 4.62 | 100.0% / 5.00 |
