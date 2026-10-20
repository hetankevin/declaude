# Codex development prose repair

Candidate v8-dev; development/validation. All 20 cases, 80 generated outputs, 320 primary and 64 audit verdicts are complete.

Net advantage is win percentage minus loss percentage. Ties contribute zero and remain in the denominator. Intervals resample cases, keeping configurations and judges together. Reversed-order audits never enter performance estimates.

| Reference | Scope | Win / tie / loss | Net advantage, pp [95% case CI] |
|---|---|---:|---:|
| none | overall | 54 / 90 / 16 | +23.8 [+8.1, +40.6] |
| none | nonproof | 28 / 84 / 16 | +9.4 [-2.3, +20.3] |
| none | category: ordinary | 7 / 19 / 6 | +3.1 [-15.6, +18.8] |
| none | category: research | 13 / 17 / 2 | +34.4 [+25.0, +43.8] |
| none | category: argument | 8 / 18 / 6 | +6.2 [-21.9, +31.2] |
| none | category: proof | 26 / 6 / 0 | +81.2 [+62.5, +100.0] |
| none | category: control | 0 / 30 / 2 | -6.2 [-18.8, +0.0] |
| none | dimension: meaning | 15 / 140 / 5 | +6.2 [-0.6, +15.0] |
| none | dimension: naturalness | 8 / 148 / 4 | +2.5 [-2.5, +8.1] |
| none | dimension: progression | 28 / 115 / 17 | +6.9 [-2.5, +16.9] |
| none | dimension: voice | 53 / 92 / 15 | +23.8 [+8.8, +40.0] |
| none | dimension: proof | 23 / 9 / 0 | +71.9 [+43.8, +100.0] |
| none | generator: astra-medium | 11 / 28 / 1 | +25.0 [+7.5, +45.0] |
| none | generator: astra-high | 14 / 22 / 4 | +25.0 [+0.0, +50.0] |
| none | generator: sol-low | 15 / 20 / 5 | +25.0 [-2.5, +50.0] |
| none | generator: luna-medium | 14 / 20 / 6 | +20.0 [-10.0, +50.0] |
| none | judge: astra-high | 28 / 44 / 8 | +25.0 [+8.8, +43.8] |
| none | judge: sol-high | 26 / 46 / 8 | +22.5 [+6.2, +38.8] |

Against none: candidate/reference material flags 3/10 in 160 primary verdicts. These count judgments, not independent errors.


| Reference | Scope | Win / tie / loss | Net advantage, pp [95% case CI] |
|---|---|---:|---:|
| v4 | overall | 43 / 95 / 22 | +13.1 [-3.1, +29.4] |
| v4 | nonproof | 43 / 68 / 17 | +20.3 [+1.6, +38.3] |
| v4 | category: ordinary | 13 / 14 / 5 | +25.0 [-31.2, +81.2] |
| v4 | category: research | 12 / 18 / 2 | +31.2 [+25.0, +37.5] |
| v4 | category: argument | 10 / 16 / 6 | +12.5 [-21.9, +40.6] |
| v4 | category: proof | 0 / 27 / 5 | -15.6 [-31.2, -3.1] |
| v4 | category: control | 8 / 20 / 4 | +12.5 [-12.5, +37.5] |
| v4 | dimension: meaning | 14 / 141 / 5 | +5.6 [-1.2, +13.1] |
| v4 | dimension: naturalness | 10 / 142 / 8 | +1.2 [-3.1, +5.6] |
| v4 | dimension: progression | 33 / 107 / 20 | +8.1 [-6.9, +21.9] |
| v4 | dimension: voice | 38 / 100 / 22 | +10.0 [-5.0, +24.4] |
| v4 | dimension: proof | 1 / 28 / 3 | -6.2 [-12.5, +0.0] |
| v4 | generator: astra-medium | 8 / 28 / 4 | +10.0 [-7.5, +30.0] |
| v4 | generator: astra-high | 7 / 29 / 4 | +7.5 [-12.5, +27.5] |
| v4 | generator: sol-low | 13 / 18 / 9 | +10.0 [-22.5, +40.0] |
| v4 | generator: luna-medium | 15 / 20 / 5 | +25.0 [-2.5, +52.5] |
| v4 | judge: astra-high | 21 / 49 / 10 | +13.8 [+0.0, +28.7] |
| v4 | judge: sol-high | 22 / 46 / 12 | +12.5 [-6.2, +31.2] |

Against v4: candidate/reference material flags 4/8 in 160 primary verdicts. These count judgments, not independent errors.

Judge agreement: 130/160, with 1 direct win/loss disagreements. Order agreement: 46/64, with 2 direct reversals.

Development data, not untouched evaluation. Two fallible Codex judges use frozen author-specific context. Audits do not enter performance. CLI token usage omits unavailable reports and is not account usage or a billing estimate.

Usage: 213 Codex attempts; 2556016 reported tokens from 213 attempts with token reports. Zero Claude calls. Failed or interrupted calls without usage are unmeasured.

summary.json contains category, dimension, generator, judge, nonproof and material-severity breakdowns. observations.json retains full and normalized grades; judge-responses.json contains exact accepted raw verdict text. responses.json contains exact synthetic writing, including reused baselines. All raw attempts, CLI envelopes and errors remain private. publication.json hashes public evidence. execution-amendment.json distinguishes the recorded freeze-time runner from later execution/report source hashes. These are development results and do not authorize promotion or consume the reserved fresh holdout.
