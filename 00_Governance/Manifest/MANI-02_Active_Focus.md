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
Last_Updated: 2026-04-22
Review_Required: Yes
---

# Active Focus

## Current Focus

- Active phase is `Phase_02_Development`.
- Active task is `TASK-0009`.
- Latest completed task is `TASK-0006`.
- Current planned development authority is `SESSION-P2-0012`.
- Latest execution development authority is `SESSION-P2-0013`.
- Latest validation development authority is `SESSION-P2-0009`.
- Continuation manifest is `MANI-03`.
- Current focus is preserving the post-follow-up `no_promotion` decision, recording the executed yaw `0` evidence, and making subsequent `TASK-0009` decisions under the repaired full-frequency `513` comparison authority.
- Current runtime baseline has passed: the TASK-0006 short-run optimization/export path produced finite traces and machine-readable summaries, and TASK-0007 repaired the saved aligned-ypr yaw `0` / yaw `90` coefficient selection path.

## Immediate next actions

- Preserve `SESSION-P2-0009` and `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/` as the machine-side route authority inherited by `TASK-0009`.
- Preserve the first official pilot matrix and its retained artifacts under `06_Assets/Generated_Artifacts/TASK-0009/`.
- Preserve the executed yaw `0` follow-up artifacts under `06_Assets/Generated_Artifacts/TASK-0009/`.
- Use the repaired full-frequency `513` comparison authority for any further `TASK-0009` screening review.
- Do not launch seed-stability reruns or a promoted long run until the baseline-authority question is resolved.
- Keep the explicit `no_promotion` decision in force unless the audit changes the authoritative comparison target.
- Keep the TASK-0007 listening files available for owner review:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/audio/`
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/listening_notes.md`
- Do not start undeclared long-run optimization outside the written `TASK-0009` plan.

## Current blocker

- The first explicit `TASK-0009` screening matrix, checkpoint policy, and comparison exports now exist, but the promoted long-run path remains deferred because the screening winner still records `baseline_not_beaten`.
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
- `TASK-0009` yaw `0` follow-up execution is now recorded under `SESSION-P2-0013`:
  - `T09-SM1-y0-s3401` passed smoke integrity checks but retained `baseline_not_beaten`
  - under the repaired full-`513` authority, `T09-P4-y0-s3401` remains the best Stage C retained run with `retained_composite = 15.37894172009149`
  - `T09-I2-y0-s3401` and `T09-I3-y0-s3401` now tie as the best Stage D retained runs with `15.417732386776184`
  - no retained run reached `paper_like_accept`
  - no Stage E seed reruns or Stage F promoted long run were launched
- Current TASK-0009 comparison risk:
  - comparison authority itself is now repaired to full `513` bins
  - the remaining risk is no longer comparison resolution drift; it is whether the current loss family can beat the authoritative baselines after that repair
- The remaining TASK-0007 human-listening gate is a separate owner-review item and should not be confused with TASK-0008 training-path preparation.
- Closed prerequisite state:
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment smoke` passed on `2026-04-17`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.front_end_bundle smoke` passed on `2026-04-17`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.baseline_renderer smoke` passed on `2026-04-17`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank smoke` passed on `2026-04-17`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation audit --indent 2` passed all machine gates except `human_listening` on `2026-04-21`; `coefficient_parity = true`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --orientation-yaw-deg 90 --iterations 24 --learning-rate 0.001 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2` passed on `2026-04-21` with `loss_reduced = true`.
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests` passed with `34` tests in the current workspace on `2026-04-21`
  - `torch` import and backward checks were repaired in `bsm_harness_py311` on `2026-04-17`.
