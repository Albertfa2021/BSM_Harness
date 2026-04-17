---
Document_ID: SESSION-P2-0006
Title: Cue Bank And Paper Aligned ITD Core
Status: Draft
Phase: Phase_02_Development
Track: Session
Maturity: Planned
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0005_Cue_Bank_And_Paper_Aligned_ITD_Core.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 05_Experiments/EXP-0001_Auditory_ILD_Python/README.md
  - 07_References/Papers/Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf
  - 03_Sessions/Distillations/DIST-0005_TASK-0004_Closure_And_TASK-0005_Handoff.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Cue Bank And Paper Aligned ITD Core

## Target Subtask

- Execute `TASK-0005` as the next Phase 02 implementation closure.
- Limit the session to:
  - cue-bank integration of the existing auditory ILD path
  - one paper-aligned differentiable ITD core

## Reference Anchors

- `05_Experiments/EXP-0001_Auditory_ILD_Python/code/auditory_ild.py`
- `07_References/Papers/Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf`
- `02_Architecture/Data/ARCH-04_Input_Output_Contracts.md`
- `02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md`
- `02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md`

## Test Standard

### Scope

- The session changes only the cue-bank and paper-aligned ITD core boundary.

### Preconditions

- `conda run -n bsm_harness_py311 python -m bsm.phase02.baseline_renderer smoke` passes.
- Active environment must be `bsm_harness_py311`.
- The session must not add residual solver code.

### Shape And Contract Checks

- The cue module must expose reusable ILD and ITD helper outputs under one response-domain interface.
- ILD helper outputs must remain aligned with the current auditory replication semantics.
- ITD helper outputs must return GCC-PHAT cross-correlation sequences inside the configured `[-tau, tau]` window.

### Numerical And Stability Checks

- ILD outputs must be finite.
- ITD helper outputs and ITD loss must be finite.
- If implemented in differentiable code, one backward pass must remain finite.

### Acceptance Checks

- One smoke command runs ILD and ITD helpers on simple binaural examples and passes.
- The session records `tau`, sample rate, and any low-frequency gating choices explicitly.

## Completion Gate

- The session closes only after the predeclared cue-bank smoke command has been run and the result has been recorded here.

## Expected Deliverables

- One project-side cue module entry.
- One paper-aligned ITD helper path.
- One smoke path for ILD and ITD verification.

## Session Start State

- `TASK-0004` baseline renderer smoke passed on `2026-04-17`.
- Baseline-renderer authority remains `bsm.phase02.baseline_renderer`.
- Implementation has not started yet in this session note.
