# Codex development prose repair

Candidate v8-dev; development/tune. All 20 cases, 80 generated outputs, 320 primary and 64 audit verdicts are complete.

Net advantage is win percentage minus loss percentage. Ties contribute zero and remain in the denominator. Intervals resample cases, keeping configurations and judges together. Reversed-order audits never enter performance estimates.

| Reference | Scope | Win / tie / loss | Net advantage, pp [95% case CI] |
|---|---|---:|---:|
| none | overall | 52 / 89 / 19 | +20.6 [+8.8, +33.8] |
| none | nonproof | 32 / 80 / 16 | +12.5 [+0.8, +24.2] |
| none | ordinary | 5 / 24 / 3 | +6.2 [-6.2, +18.8] |
| none | research | 16 / 13 / 3 | +40.6 [+28.1, +56.2] |
| none | argument | 11 / 16 / 5 | +18.8 [+6.2, +25.0] |
| none | proof | 20 / 9 / 3 | +53.1 [+31.2, +78.1] |
| none | control | 0 / 27 / 5 | -15.6 [-31.2, +0.0] |
| none | meaning | 6 / 146 / 8 | -1.2 [-6.9, +5.0] |
| none | naturalness | 12 / 144 / 4 | +5.0 [+0.0, +11.2] |
| none | progression | 37 / 112 / 11 | +16.2 [+6.9, +25.6] |
| none | voice | 52 / 94 / 14 | +23.8 [+11.9, +35.6] |
| none | proof | 20 / 11 / 1 | +59.4 [+37.5, +81.2] |
| none | astra-medium | 16 / 23 / 1 | +37.5 [+15.0, +60.0] |
| none | astra-high | 9 / 25 / 6 | +7.5 [-15.0, +32.5] |
| none | sol-low | 16 / 24 / 0 | +40.0 [+22.5, +60.0] |
| none | luna-medium | 11 / 17 / 12 | -2.5 [-32.5, +27.5] |
| none | astra-high | 25 / 48 / 7 | +22.5 [+11.2, +35.0] |
| none | sol-high | 27 / 41 / 12 | +18.8 [+5.0, +33.8] |

Against none: candidate/reference material flags 0/2 in 160 primary verdicts. These count judgments, not independent errors.

| v4 | overall | 46 / 101 / 13 | +20.6 [+8.1, +33.8] |
| v4 | nonproof | 41 / 77 / 10 | +24.2 [+10.2, +39.1] |
| v4 | ordinary | 10 / 20 / 2 | +25.0 [+0.0, +50.0] |
| v4 | research | 13 / 16 / 3 | +31.2 [+0.0, +62.5] |
| v4 | argument | 16 / 13 / 3 | +40.6 [+18.8, +62.5] |
| v4 | proof | 5 / 24 / 3 | +6.2 [-15.6, +21.9] |
| v4 | control | 2 / 28 / 2 | +0.0 [-18.8, +18.8] |
| v4 | meaning | 6 / 150 / 4 | +1.2 [-3.8, +6.2] |
| v4 | naturalness | 9 / 149 / 2 | +4.4 [+0.0, +8.8] |
| v4 | progression | 44 / 107 / 9 | +21.9 [+10.6, +35.0] |
| v4 | voice | 39 / 108 / 13 | +16.2 [+4.4, +28.7] |
| v4 | proof | 6 / 23 / 3 | +9.4 [-15.6, +37.5] |
| v4 | astra-medium | 12 / 28 / 0 | +30.0 [+12.5, +50.0] |
| v4 | astra-high | 8 / 28 / 4 | +10.0 [-12.5, +32.5] |
| v4 | sol-low | 11 / 27 / 2 | +22.5 [+2.5, +45.0] |
| v4 | luna-medium | 15 / 18 / 7 | +20.0 [-10.0, +50.0] |
| v4 | astra-high | 22 / 54 / 4 | +22.5 [+10.0, +36.2] |
| v4 | sol-high | 24 / 47 / 9 | +18.8 [+6.2, +32.5] |

Against v4: candidate/reference material flags 0/3 in 160 primary verdicts. These count judgments, not independent errors.

Judge agreement: 129/160, with 1 direct win/loss disagreements. Order agreement: 45/64, with 1 direct reversals.

Development data, not untouched evaluation. Two fallible Codex judges use frozen author-specific context. Audits do not enter performance. CLI token usage omits unavailable reports and is not account usage or a billing estimate.

Usage: 202 Codex attempts; 2341342 reported tokens from 202 attempts with token reports. Zero Claude calls. Failed or interrupted calls without usage are unmeasured.

summary.json contains category, dimension, generator, judge, nonproof and material-severity breakdowns. observations.json retains full and normalized grades; judge-responses.json contains exact accepted raw verdict text. responses.json contains exact synthetic writing, including reused baselines. All raw attempts, CLI envelopes and errors remain private. publication.json hashes public evidence. execution-amendment.json distinguishes the recorded freeze-time runner from later execution/report source hashes. These are development results and do not authorize promotion or consume the reserved fresh holdout.
