---
Document_ID: TASK-0004
Title: Baseline Coefficient Builder And Shared Renderer
Status: Stable
Phase: Phase_02_Development
Track: Task
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Phase_02_Development/SESSION-P2-0005_Baseline_Coefficient_Builder_And_Shared_Renderer.md
  - 03_Sessions/Distillations/DIST-0005_TASK-0004_Closure_And_TASK-0005_Handoff.md
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 01_Charter/Goals/CHAR-07_Phase_02_Detailed_Plan.md
  - 02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Baseline Coefficient Builder And Shared Renderer

## Scope

- Reproduce project-side baseline coefficient construction for `BSM-LS` and `BSM-MagLS`.
- Expose one shared renderer for:
  - `c_ls`
  - `c_magls`
  - later `c_joint`

## Reference Or Authority

- Direct anchors:
  - `Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py`
  - `Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py`
- Contract authority:
  - `ARCH-04` Contract 3 and Contract 6
  - `ARCH-07` Step D and Step E

## Session Policy

- Exactly one development session should be allocated to this subtask before moving on.
- That session must not add cue losses or solver code.

## Predeclared Test Standard

- Type:
  - Reference parity plus contract conformance
- Preconditions:
  - `TASK-0003` smoke path passes
  - `conda activate bsm_harness_py311`
- Required checks:
  - `c_ls` and `c_magls` share the same coefficient semantics and shape
  - shared renderer accepts baseline coefficients without special casing
  - rendered responses match expected output shape and are finite
  - `BSM-MagLS` can be rendered as the default baseline reference
- Completion gate:
  - one smoke path renders both baselines and reports finite metric-ready outputs

## Completion Evidence

- One session note with rendered output shape checks and numerical sanity checks.
- One smoke command for baseline rendering.

## Outcome

- Added `bsm.phase02.baseline_renderer` as the project-side authority for:
  - canonical baseline selection through `c_ls` and `c_magls`
  - shared rendering of baseline coefficient tensors into binaural responses
  - baseline-side metric summaries against the front-end target response `h`
- Added project-side CLI entry points for:
  - `report`
  - `smoke`
- Added project-side baseline renderer coverage in `bsm.tests.test_baseline_renderer`.
- Verified closure with:
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_front_end_bundle bsm.tests.test_baseline_renderer`
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.baseline_renderer smoke`
