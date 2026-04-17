---
Document_ID: SESSION-P2-0005
Title: Baseline Coefficient Builder And Shared Renderer
Status: Draft
Phase: Phase_02_Development
Track: Session
Maturity: Planned
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0004_Baseline_Coefficient_Builder_And_Shared_Renderer.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py
  - 07_References/Open_Source_Baselines/Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py
  - 03_Sessions/Distillations/DIST-0004_TASK-0003_Closure_And_TASK-0004_Handoff.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Baseline Coefficient Builder And Shared Renderer

## Target Subtask

- Execute `TASK-0004` as the next Phase 02 implementation closure.
- Limit the session to:
  - baseline coefficient exposure through the project-side interface
  - one shared renderer for `c_ls`, `c_magls`, and later `c_joint`

## Reference Anchors

- `07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py`
- `07_References/Open_Source_Baselines/Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py`
- `02_Architecture/Data/ARCH-04_Input_Output_Contracts.md`
- `02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md`
- `02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md`

## Test Standard

### Scope

- The session changes only the baseline coefficient builder and renderer boundary.

### Preconditions

- `conda run -n bsm_harness_py311 python -m bsm.phase02.front_end_bundle smoke` passes.
- Active environment must be `bsm_harness_py311`.
- The session must not add cue-bank or solver logic.

### Shape And Contract Checks

- `c_ls` and `c_magls` must share the same coefficient semantics and shape.
- The shared renderer must accept baseline coefficients without special casing.
- Rendered responses must match the expected direction, frequency, and ear axes.

### Numerical And Stability Checks

- Rendered baseline responses must be finite.
- `BSM-MagLS` must remain renderable as the default baseline reference.

### Acceptance Checks

- One smoke command renders both baselines and reports finite metric-ready outputs.
- Any coefficient-shape mismatch must fail loudly rather than being silently coerced.

## Completion Gate

- The session closes only after the predeclared baseline-renderer smoke command has been run and the result has been recorded here.

## Expected Deliverables

- One project-side shared renderer entry.
- One baseline-rendering smoke path.
- Recorded baseline output shapes and numerical sanity checks.

## Session Start State

- `TASK-0003` front-end smoke passed on `2026-04-17`.
- Front-end authority remains `bsm.phase02.front_end_bundle`.
- Implementation has not started yet in this session note.
