---
Document_ID: TASK-0002
Title: Asset Resolver And Environment Validator
Status: Stable
Phase: Phase_02_Development
Track: Task
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Phase_02_Development/SESSION-P2-0003_Asset_Resolver_And_Environment_Validator.md
  - 03_Sessions/Distillations/DIST-0003_TASK-0002_Asset_Closure_And_TASK-0003_Handoff.md
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 01_Charter/Goals/CHAR-07_Phase_02_Detailed_Plan.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Asset Resolver And Environment Validator

## Scope

- Build the first project-side subtask for Phase 02:
  - validate active conda environment
  - validate required asset paths
  - return one asset bundle contract for downstream modules

## Reference Or Authority

- Direct anchors:
  - `Array2Binaural/README.md`
  - `DEP-0001_Array2Binaural_Conda_Env.md`
- Contract authority:
  - `ARCH-04` Contract 1
  - `ARCH-07` Step A

## Session Policy

- Exactly one development session should be allocated to this subtask before moving on.
- That session must not implement any front-end or solver logic.

## Predeclared Test Standard

- Type:
  - Reference parity plus contract conformance
- Preconditions:
  - `conda activate bsm_harness_py311`
- Required checks:
  - active environment resolves as `bsm_harness_py311`
  - required asset paths exist or fail with explicit messages
  - returned bundle contains `array_id`, `hrtf_id`, environment name, and resolved paths
  - no imported reference tree is modified
- Completion gate:
  - one smoke command can validate the bundle without touching downstream modules

## Completion Evidence

- One session note with recorded test results.
- One runnable smoke path for resolver validation.
- Any missing asset is recorded explicitly instead of being silently ignored.

## Outcome

- Added `bsm/phase02/asset_environment.py` as the project-side asset/environment authority for Phase 02.
- Added explicit CLI entry points for:
  - `report`
  - `smoke`
  - `generate-array-sh`
- Restored the missing baseline assets required by the contract:
  - `origin_array_tf_data/Device_ATFs.h5`
  - `Easycom_array_32000Hz_o25_22samps_delay.npy`
- Added a compatibility shim so the baseline SH-generation path remains runnable under the current SciPy API.
- Verified closure with:
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_asset_environment`
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment smoke`
