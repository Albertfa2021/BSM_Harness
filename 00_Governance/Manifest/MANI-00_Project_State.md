---
Document_ID: MANI-00
Title: Project State
Status: Stable
Phase: Phase_02_Development
Track: Governance
Maturity: Consolidating
Related_Docs:
  - 00_Governance/Protocols/PROT-00_Core_Protocols.md
  - 00_Governance/Manifest/MANI-02_Active_Focus.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 04_Tasks/Active/TASK-0008_Orientation_Coefficient_Bank_And_Training_Path.md
  - 04_Tasks/Active/TASK-0007_Pre_Training_Correctness_Validation.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0009_Orientation_Training_Path_Smoke.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0010_TASK-0009_Optimization_Planning.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0013_TASK-0009_Yaw0_Followup_Execution.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0014_TASK-0009_Baseline_Not_Beaten_Diagnosis_And_Repair_Plan.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0015_TASK-0009_ILD_Metric_Unification_And_Energy_Descriptor_Repair.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0016_TASK-0009_Unified_Metric_Artifact_Refresh_And_EXP0004_Update.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0017_TASK-0009_Documentation_Refresh_And_Next_Session_Handoff.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0018_TASK-0009_Official_Full513_Rerun_And_Promotion.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0019_TASK-0009_Promoted_Yaw0_NMSE_Gap_Closure_Handoff.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0007_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md
  - 03_Sessions/Distillations/DIST-0006_TASK-0005_Closure_And_TASK-0006_Handoff.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 07_References/Open_Source_Baselines/BAS-0002_ILD_Auditory_Method.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
Last_Updated: 2026-04-23
Review_Required: Yes
---

# Project State

## Active Environment

- Required conda environment for all project-side Python development: `bsm_harness_py311`
- Activate before running project code: `conda activate bsm_harness_py311`
- Environment reference: `06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md`

- Active phase: `Phase_02_Development`
- Primary track: `Planned neural optimization campaign definition`
- Latest execution status: the official repaired-stack full-`513` rerun is complete; `paper_ild_push_v1` plus the higher-capacity solver reached stable `paper_like_accept`, and promoted long run `T09-R2-y0-s3401` is now retained
- Current baseline: `07_References/Open_Source_Baselines/Array2Binaural/`
- Supplemental baseline: `07_References/Open_Source_Baselines/ILD computer method/`
- Current objective: execute one narrow post-promotion `yaw 0` follow-up that targets the remaining `nmse` gap before any wider `TASK-0009` expansion
- Active implementation authority: `00_Governance/Manifest/MANI-03_Continuation_Authority.md`
- Active task: `04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md`
- Latest completed task: `04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md`
- Current planned development log: `03_Sessions/Phase_02_Development/SESSION-P2-0019_TASK-0009_Promoted_Yaw0_NMSE_Gap_Closure_Handoff.md`
- Latest execution development log: `03_Sessions/Phase_02_Development/SESSION-P2-0018_TASK-0009_Official_Full513_Rerun_And_Promotion.md`
- Latest validation development log: `03_Sessions/Phase_02_Development/SESSION-P2-0009_Orientation_Training_Path_Smoke.md`
- Latest distillation: `03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md`
- Runtime note:
  - `bsm_harness_py311` again supports official `torch` import and backward validation after the `2026-04-17` environment repair
- Closure note:
  - `TASK-0006` short-run optimization/export gate passed on `2026-04-20`
  - export artifacts are under `06_Assets/Generated_Artifacts/TASK-0006/20260420T034925Z/`
- Active validation note:
  - `TASK-0007` machine gates have produced the repaired yaw `0` and selected yaw `90` evidence, with human listening still pending for owner review
  - `TASK-0008` now has an executed orientation-aware smoke session recorded at `SESSION-P2-0009`
  - the accepted TASK-0008 artifact set is `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/`
  - the selected yaw `90` short run now shows actual loss reduction from `3.4457359313964844` to `3.0254967212677`
  - `TASK-0009` now has executed `yaw 90` and `yaw 0` screening evidence under `06_Assets/Generated_Artifacts/TASK-0009/`
  - `SESSION-P2-0014` records the diagnosis that baseline-not-beaten was not caused by a strict all-metrics gate alone
  - `SESSION-P2-0015` records the repair that unified ILD training/evaluation and fixed energy-descriptor plumbing
  - `SESSION-P2-0016` records the unified-metric refresh of compatible historical `TASK-0009` artifacts and the rewrite of `EXP-0004`
  - `SESSION-P2-0018` records the new official repaired-stack rerun, the first stable `paper_like_accept` result, and the promoted long run
  - `SESSION-P2-0019` records the explicit post-promotion follow-up choice:
    - prioritize `yaw 0` `nmse` gap closure first
    - defer yaw `90` transfer and energy-descriptor long-run exploration until after that narrow follow-up is judged
  - new Stage C winner is `T09-P12-y0-s3401` under `paper_ild_push_v1`
  - new Stage D winner is `T09-I5-y0-s3401`; `T09-I6-y0-s3401` shows the repaired energy-descriptor path can also reach `paper_like_accept`
  - `T09-S1-y0-s3402` and `T09-S2-y0-s3403` both preserved `paper_like_accept`, so promotion is now justified
  - promoted long run `T09-R2-y0-s3401` retained `paper_like_accept` with:
    - `ild_error = 1.7256287218571187`
    - `itd_proxy_error = 0.016510563573170753`
    - `normalized_magnitude_error = 0.30524950299696796`
    - `nmse = 1.3829925060272217`
  - `T09-R2-y0-s3401` still misses `four_down_accept` only because `nmse` remains slightly above baseline
- Formal charter status: draft
- Formal architecture status: draft
