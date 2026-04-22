---
Document_ID: TASK-0007
Title: Pre-Training Correctness Validation
Status: Active
Phase: Phase_02_Development
Track: Task
Maturity: Validating
Related_Docs:
  - 03_Sessions/Phase_02_Development/SESSION-P2-0008_Pre_Training_Correctness_Validation.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 05_Experiments/EXP-0002_Pre_Training_Correctness_Validation/README.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md
  - 04_Tasks/Active/TASK-0007A_eMagLS_Coefficient_Parity_Blocker.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# Pre-Training Correctness Validation

## Scope

- Verify project-side correctness before formal neural-network optimization.
- Treat `TASK-0007` as a validation and repair task:
  - run targeted parity, rendering, cue, solver, and audio checks
  - fix project-side implementation errors that block correctness gates
  - rerun failed gates after each fix
- Do not start real training, large ablations, new model design, or Phase 03 evaluation.

## Reference Or Authority

- Primary validation blueprint:
  - `02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md`
- Experiment protocol:
  - `05_Experiments/EXP-0002_Pre_Training_Correctness_Validation/README.md`
- Direct code anchors:
  - `07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py`
  - `07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/emagls_32kHz_dft_aligned_ypr_0_0_0.npy`
  - `07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/emagls_32kHz_dft_aligned_ypr_90_0_0.npy`
  - `07_References/Open_Source_Baselines/Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py`
  - `05_Experiments/EXP-0001_Auditory_ILD_Python/code/auditory_ild.py`
- Project-side code under validation:
  - `bsm.phase02.asset_environment`
  - `bsm.phase02.front_end_bundle`
  - `bsm.phase02.baseline_renderer`
  - `bsm.phase02.cue_bank`
  - `bsm.phase02.residual_solver`

## Predeclared Test Standard

- Type:
  - Reference parity plus contract conformance plus optimization readiness
- Preconditions:
  - active environment is `bsm_harness_py311`
  - `TASK-0006` full discovered test suite has a known passing baseline
  - Array2Binaural reference files and KU100/Easycom assets exist
- Required checks:
  - environment and asset invariant report passes
  - project `c_magls[f, m, e]` is compared against the saved Array2Binaural eMagLS filters after explicit axis canonicalization
  - renderer parity verifies numpy and torch renderers agree and reference filters render through the same steering semantics
  - cue-bank metrics are finite and traceable to their reference definitions
  - residual solver smoke still exports finite metrics after any front-end fix
  - listening WAV files are generated for human inspection and recorded in an audio manifest
- Completion gate:
  - one timestamped TASK-0007 artifact directory contains machine-readable validation summaries, audio artifacts, and a filled listening note
  - all required commands in the session note have pass/fail results recorded
  - if a direct parity difference remains, it is either fixed or explicitly documented as a blocker that prevents training

## Known Opening Risk

- A planning probe found that the saved Array2Binaural file `emagls_32kHz_dft_aligned_ypr_0_0_0.npy` has shape `(5, 2, 513)`.
- Project-side `c_magls` has shape `(513, 5, 2)`.
- After transposing the saved reference to `[frequency, microphone, ear]`, the initial observed difference was large:
  - max absolute difference approximately `3.3337`
  - mean absolute difference approximately `0.3606`
  - NMSE approximately `6.49`
- `TASK-0007` must investigate this before the project proceeds to real training.

## Expected Deliverables

- A validation harness, preferably `bsm.phase02.correctness_validation`, with an audit CLI:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation audit --indent 2
```

- Focused tests for the validation harness.
- Timestamped artifacts under:
  - `06_Assets/Generated_Artifacts/TASK-0007/<timestamp>/`
- Required artifact files:
  - `validation_summary.json`
  - `parity_metrics.json`
  - `render_metrics.json`
  - `cue_metrics.json`
  - `audio_manifest.json`
  - `listening_notes.md`
  - `audio/*.wav`
- Session evidence recorded in:
  - `03_Sessions/Phase_02_Development/SESSION-P2-0008_Pre_Training_Correctness_Validation.md`

## Acceptance Requirements

- Numeric gates:
  - all arrays under validation are finite
  - shape and axis contracts are explicit in exported summaries
  - coefficient parity failure is fixed or blocks training with a precise cause
  - renderer numpy/torch parity is within numerical precision
  - cue metrics and solver smoke outputs remain finite
- Audio gates:
  - generated WAV files are stereo, finite, non-clipping, and listed in `audio_manifest.json`
  - `listening_notes.md` records human observations for channel swap, gross coloration, image direction, unstable ITD, level imbalance, clipping, and obvious artifacts
- Documentation gates:
  - the task file remains active until all checks are recorded
  - generated artifacts are registered in `06_Assets/Generated_Artifacts/Index.md`
  - experiment registry/result tracker are updated after execution

## 2026-04-20 Execution Result

- Validation harness added at `bsm.phase02.correctness_validation`.
- Audit artifacts exported under:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260420T083829Z/`
- Audit exit status:
  - `1`
- Passing gates:
  - environment/assets
  - renderer numpy/torch parity
  - cue-bank finite validation
  - solver export readiness
  - listening WAV generation
- Blocking gates:
  - coefficient parity against saved Array2Binaural yaw `0` eMagLS reference
    - `max_abs = 3.333735227584839`
    - `mean_abs = 0.3605842888355255`
    - `nmse = 6.4899373054504395`
  - human headphone listening notes remain pending
- Regression:
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests`
  - `23` tests passed
- Residual solver smoke:
  - passed with `ok = true`
  - `initial_loss_total = 1.5917432308197021`
  - `final_loss_total = 1.561366081237793`
- Training remains disallowed until coefficient parity is repaired or the mismatch is narrowed and accepted by review.

## 2026-04-21 Blocker Execution Handoff

- The next implementation session must start from:
  - `04_Tasks/Active/TASK-0007A_eMagLS_Coefficient_Parity_Blocker.md`
- The blocker is now localized as a coefficient-contract mismatch, not an unresolved broad guess.
- `correctness_validation` currently compares project raw-like 32 kHz `c_magls` against an opaque saved Array2Binaural aligned-ypr artifact.
- A 2026-04-21 scratch port of visible `compute_emagls2_for_rotations.py` also did not reproduce `emagls_32kHz_dft_aligned_ypr_0_0_0.npy`, proving the saved file is not the visible raw eMagLS output after simple axis canonicalization.
- The blocker is not considered solved by axis canonicalization, gain scaling, ear swap, microphone permutation, or tolerance changes.
- The repaired neural-network input coefficient object must be Array2Binaural eMagLS-compatible:
  - `front_end_bundle.c_magls[f, m, e]`
  - `residual_solver.build_solver_input_pack(...).c_magls`
  - packed `solver_input_packed` channels named `c_magls_*`
- The implementation must preserve the paper-level constraint that eMagLS is solved over a global optimization grid/objective, not at a single spatial point.

## 2026-04-21 Coefficient Parity Repair Result

- `TASK-0007A` selected Option A: saved Array2Binaural aligned-ypr runtime filters are the project neural-network input coefficient authority for the static yaw `0` default.
- `front_end_bundle.c_magls[f, m, e]` now loads:
  - `07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/emagls_32kHz_dft_aligned_ypr_0_0_0.npy`
- Saved reference axes are canonicalized from `[microphone, ear, frequency]` to `[frequency, microphone, ear]`.
- `c_ls` is currently set equal to `c_magls` with explicit metadata:
  - no saved aligned-ypr LS reference is present
  - the old project-side LS object is not mixed with the repaired saved-reference `c_magls`
- `residual_solver.build_solver_input_pack(...)` uses the same repaired `c_magls`, and tests verify the packed `c_magls_*` channels reconstruct the complex coefficient values.
- New diagnostics:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation diagnose-emagls --yaw-deg 0 --indent 2
```

- Validation artifacts:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T053758Z/validation_summary.json`
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T053758Z/parity_metrics.json`
- Result:
  - yaw `0` coefficient parity now passes with `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`
  - `coefficient_parity = true`
  - renderer parity, cue-bank validation, solver export readiness, and listening WAV generation pass
  - full regression suite passes with `27` tests
  - residual solver smoke passes with finite metrics and export artifacts
- Remaining blockers:
  - `human_listening` still requires a headphone review
  - yaw `90` was not integrated in this first repair; this is superseded by the orientation-bank result below

## 2026-04-21 Head-Tracked Orientation Direction

- The project will follow the Berebi et al. 2025 head-tracked BSM-iMagLS pattern for future rotation support.
- Required direction:
  - precompute one coefficient set per supported head orientation
  - for BSM-iMagLS, generate each orientation-specific coefficient set with the DNN-based solver
  - store the resulting coefficients in an orientation-indexed coefficient bank
  - select coefficients at playback/inference time from the head-tracker yaw/pitch/roll state
- Non-goals for the next rotation step:
  - do not reuse static yaw `0` coefficients for all head poses
  - do not assume a single trained network generalizes across arbitrary HRTFs, ATFs, and orientations unless a later experiment proves that contract
  - do not perform online DNN optimization during playback
- This follow-up is separate from the repaired yaw `0` coefficient parity gate.

## 2026-04-21 Orientation Bank And yaw `90` Selection Result

- Minimum orientation coefficient bank implemented in `front_end_bundle`.
- Current supported yaw entries:
  - yaw `0`
  - yaw `90`
- Default `front_end_bundle.c_magls` remains yaw `0` for legacy/static callers.
- Rotation-specific validation and listening now select by yaw from `front_end_bundle.orientation_coefficients`.
- `rotation_90__project_bsm_magls.wav` is generated from `project_bsm_magls_yaw_90`, not from static yaw `0`.
- New validation artifact:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/`
- Result:
  - yaw `0` selected-bank parity: `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`
  - yaw `90` selected-bank parity: `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`
  - `coefficient_parity = true`
  - `renderer_parity = true`
  - `cue_bank = true`
  - `solver_export_readiness = true`
  - `listening_audio = true`
  - `human_listening = false`
- Full regression suite:
  - `28` tests passed.
- Residual solver smoke:
  - `ok = true`
  - artifact: `06_Assets/Generated_Artifacts/TASK-0006/20260421T060819Z/summary.json`
- Scope note:
  - this bank currently stores saved aligned-ypr eMagLS entries
  - DNN-solver-optimized BSM-iMagLS entries per orientation remain the next coefficient-generation task
