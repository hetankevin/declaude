# Evaluation results

Selected skill: v3. One run per case, configuration, and condition. Intervals resample paired cases, not individual assertions.

## development

| Metric | No skill | Declaude | Difference [95% interval] |
|---|---:|---:|---:|
| all | 89.2% | 100.0% | +10.81 [+5.88, +15.38] pp |
| fidelity | 100.0% | 100.0% | +0.00 [+0.00, +0.00] pp |
| style | 72.7% | 100.0% | +27.27 [+11.90, +43.33] pp |
| argument | 88.9% | 100.0% | +11.11 [+0.00, +16.67] pp |
| proof | 86.7% | 100.0% | +13.33 [+0.00, +22.22] pp |
| holistic | 3.96 | 4.71 | +0.75 [+0.42, +1.08] |
| words | 51 | 48 | — |

| Configuration | No skill assertions / holistic | Declaude assertions / holistic |
|---|---:|---:|
| astra-medium | 97.3% / 4.38 | 100.0% / 4.75 |
| sonnet-high | 89.2% / 4.00 | 100.0% / 4.62 |
| sonnet-low | 81.1% / 3.50 | 100.0% / 4.75 |

## heldout

| Metric | No skill | Declaude | Difference [95% interval] |
|---|---:|---:|---:|
| all | 89.1% | 95.3% | +6.20 [-0.83, +12.40] pp |
| fidelity | 90.0% | 93.3% | +3.33 [-3.33, +10.00] pp |
| style | 87.2% | 97.4% | +10.26 [-3.03, +28.21] pp |
| argument | 75.0% | 100.0% | +25.00 [+0.00, +66.67] pp |
| proof | 100.0% | 94.4% | -5.56 [-11.11, +0.00] pp |
| holistic | 4.04 | 4.54 | +0.50 [+0.12, +0.79] |
| words | 136 | 128 | — |

| Configuration | No skill assertions / holistic | Declaude assertions / holistic |
|---|---:|---:|
| astra-medium | 83.7% / 3.38 | 90.7% / 3.88 |
| sonnet-high | 90.7% / 4.50 | 97.7% / 4.88 |
| sonnet-low | 93.0% / 4.25 | 97.7% / 4.88 |

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
