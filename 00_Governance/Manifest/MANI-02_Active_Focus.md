---
Document_ID: MANI-02
Title: Active Focus
Status: Draft
Phase: Phase_02_Development
Track: Governance
Maturity: Consolidating
Related_Docs:
  - 04_Tasks/Active/Index.md
  - 03_Sessions/Phase_01_Discovery/Index.md
  - 03_Sessions/Phase_02_Development/Index.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
  - 04_Tasks/Active/TASK-0005_Cue_Bank_And_Paper_Aligned_ITD_Core.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0006_Cue_Bank_And_Paper_Aligned_ITD_Core.md
  - 03_Sessions/Distillations/DIST-0005_TASK-0004_Closure_And_TASK-0005_Handoff.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 07_References/Open_Source_Baselines/BAS-0002_ILD_Auditory_Method.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Active Focus

## Current Focus

- Active phase is `Phase_02_Development`.
- Active task is `TASK-0005`.
- Active development authority is `SESSION-P2-0006`.
- Continuation manifest is `MANI-03`.
- Current runtime gate is the pending cue-bank smoke path built on top of the closed `TASK-0004` baseline-renderer gate.

## Immediate next actions

- Continue only through the authority chain recorded in `MANI-03`.
- Keep work scoped to `TASK-0005` until the cue-bank smoke command exists and passes.
- Use `SESSION-P2-0006` as the active implementation log for cue-bank and ITD-core verification.
- Treat `TASK-0004` as a closed prerequisite and reuse its smoke command whenever renderer integrity needs to be revalidated.

## Current blocker

- No active blocker is recorded at handoff time.
- Prerequisite state:
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment smoke` passed on `2026-04-17`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.front_end_bundle smoke` passed on `2026-04-17`.
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.baseline_renderer smoke` passed on `2026-04-17`.
