---
Document_ID: TASK-0003
Title: Direction Grids And Front-End Bundle
Status: Stable
Phase: Phase_02_Development
Track: Task
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Phase_02_Development/SESSION-P2-0004_Direction_Grids_And_Front_End_Bundle.md
  - 03_Sessions/Distillations/DIST-0004_TASK-0003_Closure_And_TASK-0004_Handoff.md
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 01_Charter/Goals/CHAR-07_Phase_02_Detailed_Plan.md
  - 02_Architecture/Data/ARCH-03_Data_Schema.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Direction Grids And Front-End Bundle

## Scope

- Build the project-side direction-grid layer and front-end bundle that exposes:
  - optimization grid
  - evaluation grid
  - `V`
  - `h`
  - `c_ls`
  - `c_magls`

## Reference Or Authority

- Direct anchors:
  - `Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py`
  - `Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py`
- Contract authority:
  - `ARCH-03`
  - `ARCH-04` Contract 2
  - `ARCH-07` Step B and Step C

## Session Policy

- Exactly one development session should be allocated to this subtask before moving on.
- That session must not add neural optimization logic.

## Predeclared Test Standard

- Type:
  - Reference parity plus contract conformance
- Preconditions:
  - `TASK-0002` smoke path passes
  - `conda activate bsm_harness_py311`
- Required checks:
  - optimization grid matches the accepted n-design source
  - evaluation grid matches the accepted equatorial sweep semantics
  - bundle exposes all mandatory fields
  - bundle shapes are internally consistent across direction, frequency, coefficient, and ear axes
  - no `nan/inf` appears in `V`, `h`, `c_ls`, or `c_magls`
- Completion gate:
  - one smoke command prints or asserts the key shapes and passes

## Completion Evidence

- One session note with bundle shape table and test outputs.
- One smoke path that fails loudly on grid or shape inconsistency.

## Outcome

- Added `bsm.phase02.front_end_bundle` as the project-side authority for:
  - optimization-grid loading
  - evaluation-grid loading
  - front-end bundle construction
- Added project-side bundle validation and CLI entry points for:
  - `report`
  - `smoke`
- Added project-side front-end coverage in `bsm.tests.test_front_end_bundle`.
- Verified closure with:
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_front_end_bundle`
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.front_end_bundle smoke`
