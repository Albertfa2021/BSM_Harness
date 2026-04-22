---
Document_ID: ART-INDEX
Title: Generated Artifacts Index
Status: Draft
Phase: Phase_01_Discovery
Track: Asset
Maturity: Exploration
Related_Docs:
  - 05_Experiments/Registry/Result_Tracker.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md
  - 04_Tasks/Active/TASK-0007_Pre_Training_Correctness_Validation.md
  - 04_Tasks/Active/TASK-0008_Orientation_Coefficient_Bank_And_Training_Path.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# Generated Artifacts Index

| Artifact | Producer | Contents | Status |
| --- | --- | --- | --- |
| `TASK-0006/20260420T034925Z/summary.json` | `TASK-0006` | Machine-readable short-run residual solver comparison against `BSM-MagLS` | retained |
| `TASK-0006/20260420T034925Z/loss_trace.jsonl` | `TASK-0006` | Iteration-wise loss breakdown, residual norm, and `alpha` trace | retained |
| `TASK-0006/20260420T083933Z/summary.json` | `TASK-0006` | TASK-0007 rerun residual solver smoke summary; loss reduced from `1.5917432308197021` to `1.561366081237793` | retained |
| `TASK-0006/20260420T083933Z/loss_trace.jsonl` | `TASK-0006` | TASK-0007 rerun residual solver smoke loss trace | retained |
| `TASK-0007/20260420T083829Z/validation_summary.json` | `TASK-0007` | Pre-training correctness gate summary; blocks training on coefficient parity and pending human listening | retained |
| `TASK-0007/20260420T083829Z/parity_metrics.json` | `TASK-0007` | Array2Binaural eMagLS reference parity metrics after `[frequency, microphone, ear]` canonicalization | retained-blocking |
| `TASK-0007/20260420T083829Z/render_metrics.json` | `TASK-0007` | Numpy/torch renderer parity and target comparison metrics for project and saved reference coefficients | retained |
| `TASK-0007/20260420T083829Z/cue_metrics.json` | `TASK-0007` | ERB-band ILD and GCC-PHAT ITD proxy validation summaries | retained |
| `TASK-0007/20260420T083829Z/audio_manifest.json` | `TASK-0007` | Manifest for `15` finite stereo listening WAV files | retained |
| `TASK-0007/20260420T083829Z/listening_notes.md` | `TASK-0007` | Listening-note table generated for human headphone review; perceptual observations pending | pending-listener |
| `TASK-0007/20260421T053758Z/validation_summary.json` | `TASK-0007A` | Post-repair correctness gate summary; all machine gates pass except pending human listening | retained-pending-listener |
| `TASK-0007/20260421T053758Z/parity_metrics.json` | `TASK-0007A` | Saved aligned-ypr yaw `0` coefficient parity passes with `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`; yaw `90` remains a rotation-generalization follow-up | retained |
| `TASK-0007/20260421T053758Z/render_metrics.json` | `TASK-0007A` | Numpy/torch renderer parity and target comparison metrics after saved-reference coefficient repair | retained |
| `TASK-0007/20260421T053758Z/cue_metrics.json` | `TASK-0007A` | ERB-band ILD and GCC-PHAT ITD proxy validation summaries after saved-reference coefficient repair | retained |
| `TASK-0007/20260421T053758Z/audio_manifest.json` | `TASK-0007A` | Manifest for finite stereo listening WAV files after repair | retained |
| `TASK-0007/20260421T053758Z/listening_notes.md` | `TASK-0007A` | Listening-note table generated for human headphone review; perceptual observations pending | pending-listener |
| `TASK-0006/20260421T053843Z/summary.json` | `TASK-0007A` | Residual solver smoke after coefficient repair; finite metrics and artifacts present; short-run loss reduction reported but not required | retained |
| `TASK-0006/20260421T053843Z/loss_trace.jsonl` | `TASK-0007A` | Residual solver smoke loss trace after coefficient repair | retained |
| `TASK-0007/20260421T060742Z/validation_summary.json` | `TASK-0007A` | Post yaw `90` orientation-selection correctness gate summary; all machine gates pass except pending human listening | retained-pending-listener |
| `TASK-0007/20260421T060742Z/parity_metrics.json` | `TASK-0007A` | Saved aligned-ypr yaw `0` and yaw `90` selected-bank coefficient parity both pass with zero error | retained |
| `TASK-0007/20260421T060742Z/render_metrics.json` | `TASK-0007A` | Renderer parity metrics after yaw-specific project coefficient selection | retained |
| `TASK-0007/20260421T060742Z/cue_metrics.json` | `TASK-0007A` | Cue-bank metrics after yaw-specific project coefficient selection | retained |
| `TASK-0007/20260421T060742Z/audio_manifest.json` | `TASK-0007A` | Manifest for listening WAVs where `rotation_90__project_bsm_magls.wav` uses `project_bsm_magls_yaw_90` | retained |
| `TASK-0007/20260421T060742Z/listening_notes.md` | `TASK-0007A` | Listening-note table generated for second human headphone review after yaw `90` selection | pending-listener |
| `TASK-0006/20260421T060819Z/summary.json` | `TASK-0007A` | Residual solver smoke after orientation-bank implementation; finite metrics and artifacts present | retained |
| `TASK-0006/20260421T060819Z/loss_trace.jsonl` | `TASK-0007A` | Residual solver smoke loss trace after orientation-bank implementation | retained |
| `TASK-0008/20260421T065237Z/summary.json` | `TASK-0008` | Reference smoke summary for selected yaw `90`; useful prior evidence for the next TASK-0008 session, but not the final task-closure record because short-run optimization quality must still be judged in-session | retained-reference |
| `TASK-0008/20260421T065237Z/loss_trace.jsonl` | `TASK-0008` | Reference TASK-0008 orientation training-path smoke trace for the next session | retained-reference |
| `TASK-0008/20260421T065237Z/orientation_training_path.json` | `TASK-0008` | Reference selected yaw `90` training-path metadata and export shape for the next TASK-0008 session | retained-reference |
| `TASK-0008/20260421T085524Z/summary.json` | `TASK-0008` | Accepted yaw `90` orientation-training-path smoke summary; total loss reduced from `3.4457359313964844` to `3.0254967212677` after extending the short run to `24` iterations with `learning_rate = 0.001` | retained |
| `TASK-0008/20260421T085524Z/loss_trace.jsonl` | `TASK-0008` | Accepted TASK-0008 orientation training-path loss trace for the selected yaw `90` run | retained |
| `TASK-0008/20260421T085524Z/orientation_training_path.json` | `TASK-0008` | Accepted selected yaw `90` training-path metadata, solver-input summary, and export references for TASK-0009 handoff | retained |
| `TASK-0009/T09-P1-y90-s3401/summary.json` | `TASK-0009` | Pilot run 1 with `balanced_norm_v1`; best composite `0.6823205258271933` at iteration `500`; early-stopped at `900` with checkpoint refs and retained metric summary | retained-screening |
| `TASK-0009/T09-P1-y90-s3401/comparison_summary.json` | `TASK-0009` | Retained-checkpoint comparison against `BSM-MagLS` and saved aligned-ypr eMagLS reference for pilot run 1; verdict `baseline_not_beaten` | retained-screening |
| `TASK-0009/T09-P2-y90-s3401/summary.json` | `TASK-0009` | Pilot run 2 with `spatial_norm_v1`; screening winner with best composite `0.48728510709982803` at iteration `1200` | retained-screening |
| `TASK-0009/T09-P2-y90-s3401/comparison_summary.json` | `TASK-0009` | Retained-checkpoint comparison for the screening winner; verdict `baseline_not_beaten`, which triggered `no_promotion` | retained-screening |
| `TASK-0009/T09-P3-y90-s3401/summary.json` | `TASK-0009` | Pilot run 3 with `fidelity_norm_v1`; best composite `0.5424434824380371` at iteration `1200` | retained-screening |
| `TASK-0009/T09-P3-y90-s3401/comparison_summary.json` | `TASK-0009` | Retained-checkpoint comparison against declared baselines for pilot run 3; verdict `baseline_not_beaten` | retained-screening |
| `TASK-0009/T09-SM1-y0-s3401/summary.json` | `TASK-0009` | yaw `0` smoke run with `paper_ild_guarded_v1`; finite exports, checkpoint writes, and retained comparison summary confirmed before official screening | retained-smoke |
| `TASK-0009/T09-SM1-y0-s3401/comparison_summary.json` | `TASK-0009` | Smoke retained-checkpoint comparison for yaw `0`; verdict `baseline_not_beaten`, but runtime/export integrity checks passed | retained-smoke |
| `TASK-0009/T09-P4-y0-s3401/summary.json` | `TASK-0009` | Stage C loss-policy run with `balanced_norm_v1`; best official yaw `0` retained composite `13.901410750559915` | retained-screening |
| `TASK-0009/T09-P4-y0-s3401/comparison_summary.json` | `TASK-0009` | Best official yaw `0` retained-checkpoint comparison; verdict `baseline_not_beaten` | retained-screening |
| `TASK-0009/T09-P5-y0-s3401/summary.json` | `TASK-0009` | Stage C loss-policy run with `spatial_norm_v1`; retained composite `14.995125144562271` | retained-screening |
| `TASK-0009/T09-P5-y0-s3401/comparison_summary.json` | `TASK-0009` | Retained-checkpoint comparison for yaw `0` `spatial_norm_v1`; verdict `baseline_not_beaten` | retained-screening |
| `TASK-0009/T09-P6-y0-s3401/summary.json` | `TASK-0009` | Stage C loss-policy run with `paper_ild_guarded_v1`; retained composite `14.45309726173926` | retained-screening |
| `TASK-0009/T09-P6-y0-s3401/comparison_summary.json` | `TASK-0009` | Retained-checkpoint comparison for yaw `0` `paper_ild_guarded_v1`; verdict `baseline_not_beaten` | retained-screening |
| `TASK-0009/T09-P7-y0-s3401/summary.json` | `TASK-0009` | Stage C loss-policy run with `paper_ild_push_v1`; retained composite `15.025771213502482` | retained-screening |
| `TASK-0009/T09-P7-y0-s3401/comparison_summary.json` | `TASK-0009` | Retained-checkpoint comparison for yaw `0` `paper_ild_push_v1`; verdict `baseline_not_beaten` | retained-screening |
| `TASK-0009/T09-P8-y0-s3401/summary.json` | `TASK-0009` | Stage C loss-policy run with `paper_ild_push_v2`; retained composite `15.040056006176062` | retained-screening |
| `TASK-0009/T09-P8-y0-s3401/comparison_summary.json` | `TASK-0009` | Retained-checkpoint comparison for yaw `0` `paper_ild_push_v2`; verdict `baseline_not_beaten` | retained-screening |
| `TASK-0009/T09-I1-y0-s3401/summary.json` | `TASK-0009` | Stage D conservative-alpha run under `balanced_norm_v1`; retained composite `13.976813976990622` | retained-screening |
| `TASK-0009/T09-I1-y0-s3401/comparison_summary.json` | `TASK-0009` | Retained-checkpoint comparison for yaw `0` conservative-alpha variant; verdict `baseline_not_beaten` | retained-screening |
| `TASK-0009/T09-I2-y0-s3401/summary.json` | `TASK-0009` | Stage D higher-capacity run under `balanced_norm_v1`; retained composite `14.126203455407627` | retained-screening |
| `TASK-0009/T09-I2-y0-s3401/comparison_summary.json` | `TASK-0009` | Retained-checkpoint comparison for yaw `0` higher-capacity variant; verdict `baseline_not_beaten` | retained-screening |
| `TASK-0009/T09-I3-y0-s3401/summary.json` | `TASK-0009` | Stage D higher-capacity plus energy-descriptor run under `balanced_norm_v1`; retained composite `14.126203455407627` | retained-screening |
| `TASK-0009/T09-I3-y0-s3401/comparison_summary.json` | `TASK-0009` | Retained-checkpoint comparison for yaw `0` higher-capacity plus energy-descriptor variant; verdict `baseline_not_beaten` | retained-screening |
