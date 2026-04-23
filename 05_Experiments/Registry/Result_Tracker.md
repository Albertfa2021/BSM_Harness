---
Document_ID: EXP-RESULTS
Title: Result Tracker
Status: Draft
Phase: Phase_01_Discovery
Track: Experiment
Maturity: Exploration
Related_Docs:
  - 05_Experiments/Registry/EXP-Registry.md
  - 06_Assets/Generated_Artifacts/Index.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 04_Tasks/Active/TASK-0008_Orientation_Coefficient_Bank_And_Training_Path.md
Last_Updated: 2026-04-23
Review_Required: Yes
---

# Result Tracker

| Experiment | Result | Date |
| --- | --- | --- |
| `EXP-0001_Auditory_ILD_Python/` | Smoke test passed; coefficient parity to installed `gammatone` within numerical precision and constant-ratio ILD sanity check passed | 2026-04-17 |
| `TASK-0006` short-run residual solver smoke | Passed; total loss reduced from `1.6027357578277588` to `1.5498015880584717`; summary and trace exported under `06_Assets/Generated_Artifacts/TASK-0006/20260420T034925Z/` | 2026-04-20 |
| `EXP-0002_Pre_Training_Correctness_Validation/` | Executed with artifacts under `06_Assets/Generated_Artifacts/TASK-0007/20260420T083829Z/`; environment/assets, renderer parity, cue finite checks, solver readiness, and WAV generation passed; coefficient parity blocks training (`max_abs = 3.333735227584839`, `mean_abs = 0.3605842888355255`, `nmse = 6.4899373054504395` against yaw `0` reference); human listening remains pending | 2026-04-20 |
| `TASK-0006` short-run residual solver smoke rerun for `TASK-0007` | Passed; total loss reduced from `1.5917432308197021` to `1.561366081237793`; summary and trace exported under `06_Assets/Generated_Artifacts/TASK-0006/20260420T083933Z/` | 2026-04-20 |
| `TASK-0007A` eMagLS coefficient parity repair | Repaired yaw `0` coefficient parity by selecting saved Array2Binaural aligned-ypr runtime filters as the static NN input authority; post-repair audit artifacts under `06_Assets/Generated_Artifacts/TASK-0007/20260421T053758Z/`; `coefficient_parity = true` with `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`; all machine gates pass except pending human listening; yaw `90` remains a rotation-generalization follow-up | 2026-04-21 |
| `TASK-0006` residual solver smoke after `TASK-0007A` repair | Passed; finite metrics and artifacts exported under `06_Assets/Generated_Artifacts/TASK-0006/20260421T053843Z/`; short-run loss reduction is reported but not required because the saved aligned-ypr authority sets `c_ls == c_magls` | 2026-04-21 |
| `TASK-0007A` orientation bank / yaw `90` selection repair | Implemented saved-eMagLS orientation bank with yaw `0` and yaw `90`; post-selection audit artifacts under `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/`; yaw `0` and yaw `90` selected-bank parity both pass with `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`; `rotation_90__project_bsm_magls.wav` now uses `project_bsm_magls_yaw_90`; human listening remains pending | 2026-04-21 |
| `TASK-0006` residual solver smoke after orientation-bank implementation | Passed; finite metrics and artifacts exported under `06_Assets/Generated_Artifacts/TASK-0006/20260421T060819Z/` | 2026-04-21 |
| `TASK-0008` orientation-aware training-path smoke reference | Reference evidence only: selected yaw `90` coefficients were routed through solver input, short optimization, loss breakdown, and export metadata, with artifacts under `06_Assets/Generated_Artifacts/TASK-0008/20260421T065237Z/`; the next TASK-0008 session must still judge short-run optimization quality explicitly before the task can be accepted | 2026-04-21 |
| `TASK-0008` orientation-aware training-path smoke accepted run | Passed; selected yaw `90` coefficients were routed through solver input and a slightly longer short optimization with `iterations = 24` and `learning_rate = 0.001`, producing actual loss reduction from `3.4457359313964844` to `3.0254967212677`; artifacts exported under `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/` | 2026-04-21 |
| `EXP-0003_TASK-0009_Planned_Optimization_Campaign/` | Executed the first official pilot sweep under `06_Assets/Generated_Artifacts/TASK-0009/`; screening ranked `T09-P2-y90-s3401` (`best_composite = 0.48728510709982803`) ahead of `T09-P3-y90-s3401` (`0.5424434824380371`) and `T09-P1-y90-s3401` (`0.6823205258271933`), but all retained checkpoints exported `comparison_summary.json` with verdict `baseline_not_beaten`; explicit decision: `no_promotion`, so no `8000`-iteration long run was launched | 2026-04-21 |
| `EXP-0004_TASK-0009_Yaw0_Followup_Screening/` | Rewritten to the unified paper-aligned ILD metric and full-`513` optimization authority; yaw `0` baseline is now `ild = 12.72058527441395`, `itd = 0.02620715039960546`, `mag = 0.47876036643371495`, `nmse = 1.3708966970443726`; compatible historical `TASK-0009` artifacts were refreshed under the new metric, and most now beat baseline on runner composite verdict, but none satisfy `four_down_accept` or `paper_like_accept`; explicit decision remains `no_promotion`, so the next session must launch a new official rerun rather than rely on pre-unification evidence | 2026-04-22 |
| `EXP-0004_TASK-0009_Yaw0_Followup_Screening/` official repaired-stack rerun | Regression gate passed with `39` tests; official full-`513` rerun selected `paper_ild_push_v1` in Stage C, reached `paper_like_accept` in Stage D with `T09-I5-y0-s3401` and `T09-I6-y0-s3401`, stayed stable across seeds in `T09-S1-y0-s3402` and `T09-S2-y0-s3403`, and granted promotion; promoted long run `T09-R2-y0-s3401` retained `ild = 1.7256287218571187`, `itd = 0.016510563573170753`, `mag = 0.30524950299696796`, `nmse = 1.3829925060272217`, satisfying `paper_like_accept` but not `four_down_accept` | 2026-04-22 |
| `EXP-0004_TASK-0009_Yaw0_Followup_Screening/` post-promotion narrow yaw `0` follow-up | Regression gate again passed with `39` tests; narrow batch `T09-N1-y0-s3401`, `T09-N2-y0-s3401`, and `T09-N3-y0-s3401` kept the promoted route fixed and tested only light late-stage `mag` / `dmag` protection; `T09-N3-y0-s3401` reached `paper_like_accept`, but all three retained runs stayed worse than promoted authority `T09-R2-y0-s3401` on retained `nmse` and composite, so the explicit decision is `no_new_long_run` | 2026-04-23 |
| `EXP-0003_TASK-0009_Planned_Optimization_Campaign/` yaw `90` promoted transfer follow-up | Regression gate again passed with `39` tests; transfer batch `T09-Y1-y90-s3401` and `T09-Y2-y90-s3401` ported the promoted non-energy-descriptor route to yaw `90` under full `513` bins, and both reached strict yaw `90` `four_down_accept`; `T09-Y1-y90-s3401` won the batch and justified promoted long run `T09-R1-y90-s3401`, which retained `ild = 1.2432368569310537`, `itd = 0.010711959455913524`, `mag = 0.6434078756522211`, `nmse = 1.1071698665618896`; the long run becomes the best composite yaw `90` result while `T09-Y1-y90-s3401` remains the best strict four-down yaw `90` checkpoint | 2026-04-23 |
