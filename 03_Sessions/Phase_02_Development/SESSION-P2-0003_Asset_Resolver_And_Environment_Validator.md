---
Document_ID: SESSION-P2-0003
Title: Asset Resolver And Environment Validator
Status: Draft
Phase: Phase_02_Development
Track: Session
Maturity: Consolidating
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Completed/TASK-0002_Asset_Resolver_And_Environment_Validator.md
  - 03_Sessions/Distillations/DIST-0003_TASK-0002_Asset_Closure_And_TASK-0003_Handoff.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Asset Resolver And Environment Validator

## Target Subtask

- Execute `TASK-0002` as the first Phase 02 implementation closure.
- Limit the session to:
  - environment validation
  - required asset-path validation
  - asset-bundle contract output

## Reference Anchors

- `07_References/Open_Source_Baselines/Array2Binaural/README.md`
- `06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md`
- `02_Architecture/Data/ARCH-04_Input_Output_Contracts.md`
- `02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md`

## Test Standard

### Scope

- The session changes only the asset and environment module boundary.

### Preconditions

- Active environment must be `bsm_harness_py311`.
- The session must not modify imported reference source files inside `07_References/`.
- Restoring documented external assets at the required upstream paths is allowed when needed to close the smoke gate.

### Shape And Contract Checks

- The resolver output must expose:
  - `array_id`
  - `hrtf_id`
  - `environment_name`
  - required resolved asset paths

### Numerical And Stability Checks

- No downstream rendering or optimization is required in this session.
- The session still fails if:
  - path resolution produces ambiguous results
  - asset lookup silently falls back to missing files

### Acceptance Checks

- One smoke command validates the environment and required assets.
- Missing files, if any, are surfaced explicitly and recorded.
- The output bundle shape is stable enough to be consumed by the next task.

## Completion Gate

- The session closes only if the predeclared smoke path has been run and the result has been recorded here.
- If required files are missing, record the blocker here and keep the linked task active or blocked rather than widening scope.

## Expected Deliverables

- A project-side asset resolver entry point.
- A smoke test or equivalent validation command.
- Recorded results and next-step readiness for `TASK-0003`.

## Implementation Notes

- Added project-side package entry `bsm/phase02/asset_environment.py`.
- Added:
  - `inspect_asset_bundle(...)` for side-effect-free validation reports
  - `resolve_asset_bundle(...)` for strict contract enforcement
  - CLI smoke/report entry via `python -m bsm.phase02.asset_environment ...`
  - `generate_array_sh_asset(...)` and CLI `generate-array-sh` for baseline SH preprocessing
- Added a project-side compatibility shim for `scipy.special.sph_harm` so the upstream `encode_array_into_sh.py` path still runs in the current environment.
- Added standard-library unit coverage in `bsm/tests/test_asset_environment.py`.

## Verification Results

### Command 1

```bash
conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_asset_environment
```

- Result:
  - passed
  - `4` tests ran successfully
- Coverage focus:
  - success path with all required assets present
  - explicit missing-asset reporting
  - environment-name enforcement
  - SH-generation compatibility shim behavior

### Command 2

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment report
```

- Result:
  - environment resolved as `bsm_harness_py311`
  - `hrir_path` resolved to `07_References/Open_Source_Baselines/Array2Binaural/ku100_magls_sh_hrir/irsOrd5.wav`
  - bundle metadata and required contract fields were emitted
  - report surfaced two blockers explicitly:
    - missing `origin_array_tf_data/Device_ATFs.h5`
    - missing `Easycom_array_32000Hz_o25_22samps_delay.npy`

### Command 3

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment smoke
```

- Result:
  - exited non-zero by design because required assets are still missing
  - failure mode is explicit rather than silent
  - no imported reference source files were modified

### Command 4

```bash
curl -L --fail --output 07_References/Open_Source_Baselines/Array2Binaural/origin_array_tf_data/Device_ATFs.h5 https://spear2022data.blob.core.windows.net/spear-data/Device_ATFs.h5
```

- Result:
  - `Device_ATFs.h5` was restored to the baseline-expected location
  - downloaded file size is approximately `62.7M`

### Command 5

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment generate-array-sh
```

- Result:
  - generated `07_References/Open_Source_Baselines/Array2Binaural/Easycom_array_32000Hz_o25_22samps_delay.npy`
  - project-side compatibility shim was used because the current environment no longer exposes `scipy.special.sph_harm`
  - generated file size is approximately `14M`

### Command 6

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment report
```

- Result:
  - bundle reported `ok: true`
  - `array_id`, `hrtf_id`, environment name, and all required paths were emitted with no open issues

### Command 7

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.asset_environment smoke
```

- Result:
  - bundle reported `ok: true`
  - smoke gate passed with repository assets present
  - `TASK-0002` completion gate is satisfied

## Blocker Resolution

- The previously missing inputs were restored on `2026-04-17`:
  - `07_References/Open_Source_Baselines/Array2Binaural/origin_array_tf_data/Device_ATFs.h5`
  - `07_References/Open_Source_Baselines/Array2Binaural/Easycom_array_32000Hz_o25_22samps_delay.npy`
- The raw upstream SH-generation script required a compatibility shim because the current environment exposes `scipy.special.sph_harm_y` instead of `scipy.special.sph_harm`.
- The stable project-side remediation path is now:
  - `python -m bsm.phase02.asset_environment generate-array-sh`

## Next-Step Readiness

- The asset/environment module boundary is now stable enough for `TASK-0003` to consume immediately.
- `TASK-0002` can move to completed status with closure recorded through `DIST-0003`.
- `SESSION-P2-0004` is the next implementation session authority for the direction-grid and front-end bundle work.
