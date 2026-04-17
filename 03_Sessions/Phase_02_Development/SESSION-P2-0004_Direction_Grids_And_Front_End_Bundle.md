---
Document_ID: SESSION-P2-0004
Title: Direction Grids And Front-End Bundle
Status: Draft
Phase: Phase_02_Development
Track: Session
Maturity: Planned
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0003_Direction_Grids_And_Front_End_Bundle.md
  - 02_Architecture/Data/ARCH-03_Data_Schema.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py
  - 07_References/Open_Source_Baselines/Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py
  - 03_Sessions/Distillations/DIST-0003_TASK-0002_Asset_Closure_And_TASK-0003_Handoff.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Direction Grids And Front-End Bundle

## Target Subtask

- Execute `TASK-0003` as the next Phase 02 implementation closure.
- Limit the session to:
  - optimization-grid extraction
  - evaluation-grid extraction
  - front-end bundle exposure for `V`, `h`, `c_ls`, and `c_magls`

## Reference Anchors

- `07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py`
- `07_References/Open_Source_Baselines/Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py`
- `02_Architecture/Data/ARCH-03_Data_Schema.md`
- `02_Architecture/Data/ARCH-04_Input_Output_Contracts.md`
- `02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md`

## Test Standard

### Scope

- The session changes only the direction-grid and front-end bundle boundary.

### Preconditions

- `conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment smoke` passes.
- Active environment must be `bsm_harness_py311`.
- The session must not add neural optimization logic.

### Shape And Contract Checks

- The bundle must expose:
  - optimization grid
  - evaluation grid
  - `V`
  - `h`
  - `c_ls`
  - `c_magls`
- Grid-dependent axes must be internally consistent across direction, frequency, coefficient, and ear dimensions.

### Numerical And Stability Checks

- No `nan` or `inf` may appear in `V`, `h`, `c_ls`, or `c_magls`.
- Optimization-grid semantics must match the accepted n-design source.
- Evaluation-grid semantics must match the accepted equatorial sweep source.

### Acceptance Checks

- One smoke command prints or asserts the key bundle shapes and passes.
- Any grid mismatch or shape inconsistency fails loudly rather than being silently coerced.

## Completion Gate

- The session closes only after the predeclared front-end bundle smoke command has been run and the result has been recorded here.

## Expected Deliverables

- One project-side direction-grid layer.
- One front-end bundle contract object exposing the mandatory semantic fields.
- One smoke path for grid and shape verification.

## Session Start State

- `TASK-0002` prerequisite smoke passed on `2026-04-17`.
- Asset resolution authority remains `bsm.phase02.asset_environment`.
- Implementation has not started yet in this session note.
