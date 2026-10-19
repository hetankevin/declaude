# Evaluation results

Selected skill: v3. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.

## development

| Metric | none | v3 | Difference [95% interval] |
|---|---:|---:|---:|
| all | 91.6% | 97.3% | +5.68 [+2.37, +9.44] pp |
| fidelity | 99.4% | 98.9% | -0.56 [-1.43, +0.00] pp |
| style | 78.2% | 96.4% | +18.18 [+7.27, +28.46] pp |
| argument | 93.3% | 86.7% | -6.67 [-10.00, +0.00] pp |
| proof | 92.0% | 100.0% | +8.00 [+0.00, +13.33] pp |
| holistic | 4.12 | 4.51 | +0.39 [+0.14, +0.65] |
| words | 54 | 42 | — |

| Configuration | none assertions / holistic | v3 assertions / holistic |
|---|---:|---:|
| astra-high | 100.0% / 4.38 | 100.0% / 4.62 |
| astra-medium | 94.6% / 4.38 | 97.3% / 4.62 |
| fable | 81.1% / 3.75 | 100.0% / 4.88 |
| haiku | 86.5% / 3.88 | 89.2% / 4.00 |
| luna-medium | 89.2% / 4.00 | 94.6% / 3.88 |
| opus-low | 97.3% / 4.75 | 100.0% / 4.62 |
| opus-xhigh | 97.3% / 4.75 | 97.3% / 4.75 |
| sol-low | 100.0% / 4.38 | 100.0% / 4.62 |
| sonnet-high | 89.2% / 3.88 | 97.3% / 4.50 |
| sonnet-low | 81.1% / 3.12 | 97.3% / 4.62 |

## heldout

| Metric | none | v3 | Difference [95% interval] |
|---|---:|---:|---:|
| all | 87.7% | 91.2% | +3.49 [-1.67, +8.84] pp |
| fidelity | 91.5% | 95.5% | +4.00 [+0.48, +8.33] pp |
| style | 80.8% | 90.0% | +9.23 [-0.83, +25.83] pp |
| argument | 75.0% | 87.5% | +12.50 [-10.00, +30.00] pp |
| proof | 98.3% | 81.7% | -16.67 [-26.67, -6.67] pp |
| holistic | 3.89 | 4.26 | +0.38 [+0.19, +0.60] |
| words | 130 | 128 | — |

| Configuration | none assertions / holistic | v3 assertions / holistic |
|---|---:|---:|
| astra-high | 83.7% / 3.38 | 93.0% / 4.38 |
| astra-medium | 83.7% / 3.38 | 88.4% / 4.00 |
| fable | 93.0% / 4.38 | 97.7% / 4.75 |
| haiku | 83.7% / 3.62 | 86.0% / 3.88 |
| luna-medium | 74.4% / 3.12 | 67.4% / 2.88 |
| opus-low | 83.7% / 3.75 | 95.3% / 4.38 |
| opus-xhigh | 95.3% / 4.62 | 100.0% / 5.00 |
| sol-low | 88.4% / 3.62 | 88.4% / 3.88 |
| sonnet-high | 95.3% / 4.50 | 95.3% / 4.50 |
| sonnet-low | 95.3% / 4.50 | 100.0% / 5.00 |

## Development A/B selection

The initial and revised skill versions were compared on Sonnet low and Astra medium only. These cases were available for selection and are not held out.

| Subset | Version | Assertions | Holistic |
|---|---|---:|---:|
| tune | none | 89.5% | 3.62 |
| tune | v1 | 100.0% | 4.38 |
| tune | v2 | 100.0% | 4.50 |
| tune | v3 | 100.0% | 4.50 |
| validation | none | 88.9% | 4.12 |
| validation | v1 | 94.4% | 4.62 |
| validation | v2 | 91.7% | 4.50 |
| validation | v3 | 100.0% | 4.88 |
