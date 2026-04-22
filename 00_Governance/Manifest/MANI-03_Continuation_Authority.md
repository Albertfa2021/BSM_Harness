---
Document_ID: MANI-03
Title: Continuation Authority
Status: Draft
Phase: Phase_02_Development
Track: Governance
Maturity: Consolidating
Related_Docs:
  - Agent.md
  - 00_Governance/Manifest/MANI-00_Project_State.md
  - 00_Governance/Manifest/MANI-02_Active_Focus.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 04_Tasks/Active/TASK-0008_Orientation_Coefficient_Bank_And_Training_Path.md
  - 04_Tasks/Active/TASK-0007_Pre_Training_Correctness_Validation.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0009_Orientation_Training_Path_Smoke.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0010_TASK-0009_Optimization_Planning.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0011_TASK-0009_Screening_Execution.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0012_TASK-0009_Yaw0_Followup_Planning.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0013_TASK-0009_Yaw0_Followup_Execution.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 05_Experiments/EXP-0002_Pre_Training_Correctness_Validation/README.md
  - 05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0007_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md
  - 04_Tasks/Completed/TASK-0005_Cue_Bank_And_Paper_Aligned_ITD_Core.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0006_Cue_Bank_And_Paper_Aligned_ITD_Core.md
  - 03_Sessions/Distillations/DIST-0006_TASK-0005_Closure_And_TASK-0006_Handoff.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
Last_Updated: 2026-04-22
Review_Required: Yes
---

# Continuation Authority

## Purpose

- This manifest entry defines the minimum document set required for continuation by docs alone.
- An agent starting from `Agent.md` should treat this file as the current implementation authority record for active work.

## Current Implementation Authority

- Root entry:
  - `Agent.md`
- Project state authority:
  - `00_Governance/Manifest/MANI-00_Project_State.md`
- Active focus authority:
  - `00_Governance/Manifest/MANI-02_Active_Focus.md`
- Latest completed task authority:
  - `04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md`
- Active task authority:
  - `04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md`
- Active validation and orientation-bank context:
  - `02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md`
  - `04_Tasks/Active/TASK-0008_Orientation_Coefficient_Bank_And_Training_Path.md`
- Active experiment protocol:
  - `05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md`
- Latest validation development log:
  - `03_Sessions/Phase_02_Development/SESSION-P2-0009_Orientation_Training_Path_Smoke.md`
- Planned next development log:
  - `03_Sessions/Phase_02_Development/SESSION-P2-0012_TASK-0009_Yaw0_Followup_Planning.md`
- Latest execution development log:
  - `03_Sessions/Phase_02_Development/SESSION-P2-0013_TASK-0009_Yaw0_Followup_Execution.md`
- Latest closure distillation:
  - `03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md`
- Phase 02 implementation blueprint:
  - `02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md`

## Active Continuation State

- Active phase:
  - `Phase_02_Development`
- Current task:
  - `TASK-0009`
- Current task status:
  - first official yaw `90` screening and the written yaw `0` follow-up screening are both executed; explicit decision remains `no_promotion`; comparison authority is now repaired to full-frequency `513` and promoted long run remains deferred
- Current session authority:
  - `03_Sessions/Phase_02_Development/SESSION-P2-0013_TASK-0009_Yaw0_Followup_Execution.md`
- Environment authority:
  - `bsm_harness_py311`

## Closed Prerequisite Verification

- Unit verification:

```bash
conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_asset_environment
```

- Asset generation helper:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment generate-array-sh
```

- Asset smoke gate:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment smoke
```

- Front-end bundle smoke gate:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.front_end_bundle smoke
```

- Baseline renderer smoke gate:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.baseline_renderer smoke
```

- Cue-bank regression gate:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank smoke
```

- Residual solver short-run export gate:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

- Full discovered test suite:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

## Current Handoff State

- `TASK-0005` cue-bank smoke gate passed on `2026-04-17` and the task can now be treated as closed.
- The project-side cue boundary now exists through:
  - `bsm.phase02.cue_bank`
- Closed evidence for the cue-bank gate is:
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_baseline_renderer bsm.tests.test_cue_bank`
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_cue_bank.CueBankTests.test_torch_itd_loss_supports_finite_backward_pass`
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank smoke`
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank report --baseline-name BSM-MagLS`
- Environment follow-up:
  - `torch` import and backward checks in `bsm_harness_py311` were repaired on `2026-04-17` by cleaning the mixed `pytorch`/`torch` installation and restoring the OpenMP runtime.
- `TASK-0006` short-run optimization/export gate passed on `2026-04-20`.
- Export artifacts are recorded at:
  - `06_Assets/Generated_Artifacts/TASK-0006/20260420T034925Z/summary.json`
  - `06_Assets/Generated_Artifacts/TASK-0006/20260420T034925Z/loss_trace.jsonl`
- TASK-0007 repaired the saved aligned-ypr yaw `0` coefficient authority and added selected-bank yaw `90` parity.
- TASK-0008 now has an accepted orientation-aware smoke run:
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --orientation-yaw-deg 90 --iterations 24 --learning-rate 0.001 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2`
  - `initial_loss_total = 3.4457359313964844`
  - `final_loss_total = 3.0254967212677`
  - `loss_reduced = true`
  - artifacts:
    - `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/summary.json`
    - `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/loss_trace.jsonl`
    - `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/orientation_training_path.json`
- Current opening risk:
  - the first `TASK-0009` screening matrix now exists, but long-run optimization would still be premature because the screening winner did not beat the declared retained baselines.
- `TASK-0009` screening execution is now recorded at:
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P1-y90-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P2-y90-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P3-y90-s3401/`
- `TASK-0009` yaw `0` follow-up execution is now recorded at:
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-SM1-y0-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P4-y0-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P5-y0-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P6-y0-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P7-y0-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P8-y0-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-I1-y0-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-I2-y0-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-I3-y0-s3401/`
- Screening ranking and decision:
  - `T09-P2-y90-s3401` won with `best_composite = 0.48728510709982803`
  - `T09-P3-y90-s3401` followed with `0.5424434824380371`
  - `T09-P1-y90-s3401` followed with `0.6823205258271933`
  - all retained checkpoints recorded `baseline_not_beaten`
  - decision: `no_promotion`
- yaw `0` follow-up ranking and decision:
  - under the repaired full-`513` authority, Stage C best retained run remains `T09-P4-y0-s3401` with `retained_composite = 15.37894172009149`
  - Stage D did not improve on that result; best Stage D retained runs are `T09-I2-y0-s3401` and `T09-I3-y0-s3401`, tied at `15.417732386776184`
  - all retained checkpoints again recorded `baseline_not_beaten`
  - no run reached `paper_like_accept`
  - decision: `no_promotion`
- Current comparison-authority risk:
  - `EXP-0004` declares a yaw `0` baseline to beat of `ild = 9.526687421752532`, `itd = 0.02620715039960546`, `mag = 0.47876036643371495`, `nmse = 1.3708966970443726`
  - owner decision selected full-frequency `513` as the required comparison authority
  - `task09_runner` comparison export was repaired so sliced pilot runs now evaluate retained checkpoints and baselines on the full selected-orientation bundle
  - existing `TASK-0009` `comparison_summary.json` files were refreshed with the repaired authority
- The remaining owner decision is explicitly deferred to the next session:
  - decide whether yaw `0` should be rerun under the repaired authority
  - decide whether yaw `90` should be revisited under the same full-frequency comparison policy
  - or open a blocker if the current loss family still cannot beat the authoritative baselines

## Continuation Rule

- A continuation request such as "按照实施文档和开发日志继续" should resolve through this chain:
  - `Agent.md`
  - `MANI-00`
  - `MANI-02`
  - `MANI-03`
  - active `TASK-0009`
  - `TASK-0008`, `TASK-0007`, and `TASK-0007A` as route-validation context
  - `ARCH-08`
  - `ARCH-09`
  - `EXP-0003`
  - `EXP-0004`
  - latest validation `SESSION-P2-0009`
  - latest planning/execution `SESSION-P2-0013`
- The next session should use the repaired full-`513` comparison authority, then decide from recorded evidence whether yaw `0` should be rerun, whether yaw `90` should be revisited, or whether a blocker should be opened on the loss policy itself.
- Large-scale planned optimization must continue to wait until a `TASK-0009` profile earns promotion.
