---
Document_ID: MANI-02
Title: Active Focus
Status: Draft
Phase: Phase_02_Development
Track: Governance
Maturity: Consolidating
Related_Docs:
  - 04_Tasks/Active/Index.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 04_Tasks/Active/TASK-0008_Orientation_Coefficient_Bank_And_Training_Path.md
  - 04_Tasks/Active/TASK-0007_Pre_Training_Correctness_Validation.md
  - 04_Tasks/Active/TASK-0007A_eMagLS_Coefficient_Parity_Blocker.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0009_Orientation_Training_Path_Smoke.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0010_TASK-0009_Optimization_Planning.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0011_TASK-0009_Screening_Execution.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0012_TASK-0009_Yaw0_Followup_Planning.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0013_TASK-0009_Yaw0_Followup_Execution.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0014_TASK-0009_Baseline_Not_Beaten_Diagnosis_And_Repair_Plan.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0015_TASK-0009_ILD_Metric_Unification_And_Energy_Descriptor_Repair.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0016_TASK-0009_Unified_Metric_Artifact_Refresh_And_EXP0004_Update.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0017_TASK-0009_Documentation_Refresh_And_Next_Session_Handoff.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0018_TASK-0009_Official_Full513_Rerun_And_Promotion.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0019_TASK-0009_Promoted_Yaw0_NMSE_Gap_Closure_Handoff.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0020_TASK-0009_Post_Promotion_Yaw0_NMSE_Followup_Execution.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 05_Experiments/EXP-0002_Pre_Training_Correctness_Validation/README.md
  - 05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Phase_01_Discovery/Index.md
  - 03_Sessions/Phase_02_Development/Index.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0007_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md
  - 03_Sessions/Distillations/DIST-0006_TASK-0005_Closure_And_TASK-0006_Handoff.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 07_References/Open_Source_Baselines/BAS-0002_ILD_Auditory_Method.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
Last_Updated: 2026-04-23
Review_Required: Yes
---

# Active Focus

## Current Focus

- Active phase is `Phase_02_Development`.
- Active task is `TASK-0009`.
- Latest completed task is `TASK-0006`.
- Current planned development authority is `SESSION-P2-0020`.
- Latest execution development authority is `SESSION-P2-0020`.
- Latest validation development authority is `SESSION-P2-0009`.
- Continuation manifest is `MANI-03`.
- Current focus is continuing `TASK-0009` from the promoted yaw `0` result after the narrow post-promotion NMSE follow-up batch, under the unified paper-aligned ILD metric, repaired energy-descriptor plumbing, and full-frequency `513` optimization authority.
- Current runtime baseline has passed: the TASK-0006 short-run optimization/export path produced finite traces and machine-readable summaries, and TASK-0007 repaired the saved aligned-ypr yaw `0` / yaw `90` coefficient selection path.

## Immediate next actions

- Preserve `SESSION-P2-0009` and `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/` as the machine-side route authority inherited by `TASK-0009`.
- Preserve the first official pilot matrix, the original yaw `0` follow-up artifacts, and the new official repaired-stack rerun artifacts under `06_Assets/Generated_Artifacts/TASK-0009/`.
- Use the unified full-frequency `513` optimization and comparison authority for any further `TASK-0009` work.
- Treat the refreshed `EXP-0004` thresholds as the only current baseline authority for yaw `0`.
- Use `SESSION-P2-0020` plus `SESSION-P2-0018` and `T09-R2-y0-s3401` as the current continuation authority set.
- Keep the new narrow follow-up batch summary available:
  - `06_Assets/Generated_Artifacts/TASK-0009/yaw0_nmse_followup_SESSION-P2-0020_y0_s3401/comparison_summary.json`
- The narrow `yaw 0` follow-up has now been executed and did not justify a new long run.
- Current fallback priorities after the failed narrow follow-up are:
  - transfer the promoted configuration to yaw `90`
  - evaluate whether the accepted repaired energy-descriptor variant deserves its own long run
- Keep the TASK-0007 listening files available for owner review:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/audio/`
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/listening_notes.md`
- Do not start undeclared long-run optimization outside the written `TASK-0009` plan.

## Current blocker

- No hard blocker currently prevents promoted `TASK-0009` follow-up work.
- The coefficient parity blocker from `TASK-0007A` is repaired for saved Array2Binaural aligned-ypr yaw `0`.
- yaw `90` saved-eMagLS direct parity now passes through the selected orientation-bank entry.
- `TASK-0008` selected-yaw short-run quality is explicitly recorded as passing and is now the inherited route authority for `TASK-0009`:
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --orientation-yaw-deg 90 --iterations 24 --learning-rate 0.001 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2`
  - artifacts: `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/`
  - loss: `3.4457359313964844 -> 3.0254967212677`
- `TASK-0009` has now been defined as the owner of:
  - run matrix
  - checkpoint policy
  - seed policy
  - long-run logging
  - retained baseline comparison
  - screening-based promotion decisions
- `TASK-0009` screening execution is now recorded under `SESSION-P2-0011` with an explicit `no_promotion` decision:
  - `T09-P2-y90-s3401` won the pilot sweep with `best_composite = 0.48728510709982803`
  - all retained checkpoints exported `comparison_summary.json`
  - all retained checkpoints recorded `baseline_not_beaten`
  - no `T09-R1-y90-s3401` long run was launched
- The next written execution authority is now:
  - `03_Sessions/Phase_02_Development/SESSION-P2-0012_TASK-0009_Yaw0_Followup_Planning.md`
  - `05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md`
- `TASK-0009` post-follow-up diagnosis and repair are now recorded under `SESSION-P2-0014` and `SESSION-P2-0015`:
  - ILD training/evaluation are now unified around one paper-aligned banded metric
  - energy-descriptor plumbing is now real and artifact-visible
  - full discovered test suite passed at `39` tests after the repair
- `TASK-0009` experiment authority refresh is now recorded under `SESSION-P2-0016`:
  - `EXP-0004` baseline thresholds were rewritten to the unified metric
  - all screening commands were rewritten to `--max-frequency-bins 513`
  - compatible historical `TASK-0009` artifacts were refreshed under the new metric
  - refreshed historical runs now generally beat baseline on runner composite verdict
  - but none of them satisfy `four_down_accept` or `paper_like_accept`
  - `T09-I3-y0-s3401` remains an old-format pre-repair artifact because its checkpoint expects the old `14`-channel solver input
- `TASK-0009` official repaired-stack rerun is now recorded under `SESSION-P2-0018`:
  - Stage C selected `paper_ild_push_v1` as the best loss profile
  - Stage D winner `T09-I5-y0-s3401` reached `paper_like_accept`
  - repaired energy-descriptor variant `T09-I6-y0-s3401` also reached `paper_like_accept` with `solver_input_packed_shape = [513, 5, 15]`
  - Stage E seed reruns `T09-S1-y0-s3402` and `T09-S2-y0-s3403` both stayed `paper_like_accept`
  - promoted long run `T09-R2-y0-s3401` retained `paper_like_accept`, though it still misses `four_down_accept` because `nmse = 1.3829925060272217` remains slightly above baseline
- `SESSION-P2-0020` executed the required narrow post-promotion batch:
  - `T09-N1-y0-s3401` kept the promoted profile as a short-horizon control and retained `nmse = 1.4522264003753662`
  - `T09-N2-y0-s3401` added late `mag` protection and retained `nmse = 1.4740402698516846`
  - `T09-N3-y0-s3401` added late `dmag` protection and retained `nmse = 1.4422805309295654`
  - `T09-N3-y0-s3401` reached `paper_like_accept`, but none of the narrow retained runs improved on promoted authority `T09-R2-y0-s3401`
  - explicit decision: `no_new_long_run`
- Current TASK-0009 engineering risk:
  - the key open question is no longer yaw `0` narrow follow-up authorization
  - the key open question is which fallback route is worth the next official budget after the narrow yaw `0` batch failed to beat promoted authority
- The remaining TASK-0007 human-listening gate is a separate owner-review item and should not be confused with TASK-0008 training-path preparation.
- Closed prerequisite state:
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment smoke` passed on `2026-04-17`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.front_end_bundle smoke` passed on `2026-04-17`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.baseline_renderer smoke` passed on `2026-04-17`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank smoke` passed on `2026-04-17`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation audit --indent 2` passed all machine gates except `human_listening` on `2026-04-21`; `coefficient_parity = true`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --orientation-yaw-deg 90 --iterations 24 --learning-rate 0.001 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2` passed on `2026-04-21` with `loss_reduced = true`.
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests` passed with `39` tests in the current workspace on `2026-04-22`
  - `torch` import and backward checks were repaired in `bsm_harness_py311` on `2026-04-17`.
