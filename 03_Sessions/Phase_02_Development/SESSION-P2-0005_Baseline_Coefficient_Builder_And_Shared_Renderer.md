---
Document_ID: SESSION-P2-0005
Title: Baseline Coefficient Builder And Shared Renderer
Status: Draft
Phase: Phase_02_Development
Track: Session
Maturity: Consolidating
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
- `TASK-0004` implementation was completed in this session note.

## Implementation Notes

- Added project-side shared renderer authority in `bsm.phase02.baseline_renderer`.
- Added project-side baseline helpers for:
  - canonical baseline selection through `c_ls` and `c_magls`
  - one shared renderer entry that consumes any coefficient tensor with the baseline bundle shape
  - baseline-side metric summaries against the front-end target response `h`
- Added CLI entry points for:
  - `python -m bsm.phase02.baseline_renderer report`
  - `python -m bsm.phase02.baseline_renderer smoke`
- Added project-side coverage in `bsm.tests.test_baseline_renderer`.
- The shared renderer now uses the front-end bundle semantics directly:
  - input: `V[d, f, m]` and coefficients `[f, m, e]`
  - output: response `[d, f, e]`
- Coefficient-shape mismatch now raises an explicit error instead of coercing axes silently.
- No cue-bank, ITD, residual solver, or joint-coefficient logic was added in this session.

## Verification Results

### Command 1

```bash
conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_front_end_bundle bsm.tests.test_baseline_renderer
```

- Result:
  - passed
  - `8` tests ran successfully
- Coverage focus:
  - front-end bundle regression guard
  - baseline-name resolution
  - shared renderer acceptance for both `BSM-LS` and `BSM-MagLS`
  - explicit coefficient-shape failure behavior
  - smoke summary coverage for both baselines

### Command 2

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.baseline_renderer smoke
```

- Result:
  - passed
  - rendered both `BSM-LS` and `BSM-MagLS`
  - reported finite metric-ready outputs with no open issues
- Recorded smoke shapes:
  - `V`: `[72, 513, 5]`
  - `h`: `[72, 513, 2]`
  - `c_ls`: `[513, 5, 2]`
  - `c_magls`: `[513, 5, 2]`
  - rendered `BSM-LS` response: `[72, 513, 2]`
  - rendered `BSM-MagLS` response: `[72, 513, 2]`
- Numerical summary:
  - all bundle tensors remained finite
  - both rendered baseline responses remained finite
  - smoke metrics against `h` were emitted for both baselines
  - recorded `nmse_to_target`:
    - `BSM-LS`: `0.6732804579872262`
    - `BSM-MagLS`: `1.8074381736160647`

## Completion Gate Result

- The predeclared `TASK-0004` baseline-renderer smoke command now exists and passes.
- The session-level completion gate for `TASK-0004` is satisfied.

## Next-Step Readiness

- The project-side shared renderer boundary is now stable enough for `TASK-0005` to consume.
- Manifest and task-list promotion should wait for the next distillation or closure pass rather than being inferred directly from this session note.
