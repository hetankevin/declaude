# Evaluation results

Selected skill: v4. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.

## development

| Metric | v3 | v4 | Difference [95% interval] |
|---|---:|---:|---:|
| all | 97.6% | 98.1% | +0.54 [-1.25, +2.43] pp |
| fidelity | 98.3% | 98.9% | +0.56 [-1.54, +2.17] pp |
| style | 95.5% | 96.4% | +0.91 [-5.00, +6.67] pp |
| argument | 96.7% | 96.7% | +0.00 [+0.00, +0.00] pp |
| proof | 100.0% | 100.0% | +0.00 [+0.00, +0.00] pp |
| holistic | 4.64 | 4.72 | +0.09 [-0.01, +0.18] |
| words | 42 | 50 | — |

| Configuration | v3 assertions / holistic | v4 assertions / holistic |
|---|---:|---:|
| astra-high | 100.0% / 5.00 | 100.0% / 4.88 |
| astra-medium | 100.0% / 4.88 | 100.0% / 4.88 |
| fable | 97.3% / 4.62 | 100.0% / 5.00 |
| haiku | 89.2% / 4.00 | 91.9% / 4.12 |
| luna-medium | 94.6% / 4.00 | 94.6% / 4.25 |
| opus-low | 100.0% / 4.62 | 100.0% / 5.00 |
| opus-xhigh | 100.0% / 5.00 | 100.0% / 5.00 |
| sol-low | 100.0% / 4.88 | 100.0% / 4.88 |
| sonnet-high | 97.3% / 4.62 | 97.3% / 4.62 |
| sonnet-low | 97.3% / 4.75 | 97.3% / 4.62 |

## Development A/B selection

The initial and revised skill versions were compared on Sonnet low and Astra medium only. These cases were available for selection and are not held out.

| Subset | Version | Assertions | Holistic |
|---|---|---:|---:|
