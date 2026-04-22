---
Document_ID: TASK-0007A
Title: eMagLS Coefficient Parity Blocker Repair
Status: Review
Phase: Phase_02_Development
Track: Task
Maturity: Validating
Related_Docs:
  - 04_Tasks/Active/TASK-0007_Pre_Training_Correctness_Validation.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0008_Pre_Training_Correctness_Validation.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 02_Architecture/Data/ARCH-03_Data_Schema.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 05_Experiments/EXP-0002_Pre_Training_Correctness_Validation/README.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py
  - 07_References/Open_Source_Baselines/Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py
  - 07_References/Papers/Madmoni 等 - 2025 - Design and Analysis of Binaural Signal Matching with Arbitrary Microphone Arrays and Listener Head R.pdf
  - 07_References/Papers/Berebi 等 - 2025 - BSM-iMagLS ILD Informed Binaural Signal Matching for Reproduction with Head-Mounted Microphone Arra.pdf
  - 07_References/Papers/E-library page.pdf
Last_Updated: 2026-04-21
Review_Required: Yes
---

# eMagLS Coefficient Parity Blocker Repair

## Purpose

This document records the located `TASK-0007` coefficient-parity blocker and its 2026-04-21 implementation repair.

The blocker to repair is direct coefficient parity: saved Array2Binaural yaw `0` eMagLS filters canonicalize cleanly to `[frequency, microphone, ear]`, but still differ greatly from project `front_end_bundle.c_magls`. Training remains disallowed until the coefficient object that enters the neural network is proven to use the same Array2Binaural eMagLS parameter semantics.

Diagnosis status as of 2026-04-21:

- The immediate cause has been located.
- The yaw `0` implementation repair has been applied and validated.
- Do not restart future work from broad speculation; begin from the conclusions in `Problem Location` and `Implementation Result`.

## Implementation Result

Date: 2026-04-21

Selected authority:

- Option A: saved Array2Binaural aligned-ypr runtime filters are the neural-network input coefficient authority for the static yaw `0` default.
- Rationale: the checked-in `emagls_32kHz_dft_aligned_ypr_*` files are the filters consumed by the Array2Binaural evaluation/runtime path, while their exact generation script is absent from the checked-in reference tree.

Code changes:

- Added `bsm.phase02.array2binaural_emagls`.
  - Loads saved aligned-ypr eMagLS references.
  - Canonicalizes `[microphone, ear, frequency]` to `[frequency, microphone, ear]`.
  - Provides a visible raw Array2Binaural 48 kHz / 1536 diagnostic builder that remains explicitly distinguished from the opaque aligned-ypr artifact.
- Updated `bsm.phase02.front_end_bundle`.
  - Default `front_end_bundle.c_magls[f, m, e]` now loads `emagls_32kHz_dft_aligned_ypr_0_0_0.npy`.
  - `c_ls` is set to the same coefficient object as a documented compatibility baseline because no saved aligned-ypr LS reference is present.
  - Summary metadata now records `c_ls_source`, `c_magls_source`, `emagls_compute_sample_rate_hz`, `emagls_nfft`, `emagls_reference_yaw_deg`, reference path, and reference hash.
- Updated `bsm.phase02.correctness_validation`.
  - The audit records the selected coefficient authority.
  - `diagnose-emagls` reports the resolved coefficient-contract distinction.
  - yaw `90` remains explicitly recorded as a rotation-generalization blocker for the static default.
- Updated `bsm.phase02.residual_solver`.
  - `build_solver_input_pack(...)` continues to use `front_end_bundle.c_magls`.
  - The smoke gate now validates finite metrics and export artifacts; short-run loss reduction is reported but not required when `c_ls == c_magls`.

Validation:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation diagnose-emagls --yaw-deg 0 --indent 2
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation audit --indent 2
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

Results:

- yaw `0` coefficient parity against saved aligned-ypr reference:
  - `max_abs = 0.0`
  - `mean_abs = 0.0`
  - `nmse = 0.0`
  - `coefficient_parity = true`
- Full tests:
  - `27` tests passed.
- TASK-0007 audit:
  - `environment_and_assets = true`
  - `coefficient_parity = true`
  - `renderer_parity = true`
  - `cue_bank = true`
  - `solver_export_readiness = true`
  - `listening_audio = true`
  - `human_listening = false`
- Residual solver smoke:
  - `ok = true`
  - finite metrics and export artifacts present
  - `loss_reduced = false` is expected and reported, not blocking, because no saved aligned-ypr LS reference exists and `c_ls == c_magls`.

New artifacts:

- `06_Assets/Generated_Artifacts/TASK-0007/20260421T053758Z/validation_summary.json`
- `06_Assets/Generated_Artifacts/TASK-0007/20260421T053758Z/parity_metrics.json`
- `06_Assets/Generated_Artifacts/TASK-0006/20260421T053843Z/summary.json`

Remaining limitations:

- yaw `90` direct parity does not pass for the static yaw `0` default and is now an explicit rotation-generalization blocker.
- Training remains disallowed only because the human-listening gate is still pending, not because coefficient parity failed.

## Follow-Up Requirement: Head-Tracked Orientation Coefficient Bank

Decision recorded on 2026-04-21:

- The project should follow the Berebi et al. 2025 head-tracked BSM-iMagLS interpretation:
  - each supported head orientation gets its own coefficient set
  - for BSM-iMagLS, each coefficient set is generated by solving the per-orientation objective with the DNN-based solver
  - playback/inference should select the precomputed coefficient set from head-tracker yaw/pitch/roll state, rather than training online during playback
- This is not a single global network that maps arbitrary orientation to coefficients.
- This is also not a static yaw `0` coefficient reused for all rotations.
- The next rotation-generalization task must define:
  - orientation grid, at minimum yaw `0` and yaw `90`
  - coefficient-bank schema keyed by yaw/pitch/roll
  - DNN-solver export contract for each orientation
  - front-end selection API for `c_magls` / `c_imagls` by orientation
  - validation parity for saved or generated references per orientation
  - listening artifacts that compare static yaw `0`, selected yaw `90`, and target/reference renderings

## Orientation Bank Implementation Result

Date: 2026-04-21

Implemented minimum orientation coefficient bank:

- `front_end_bundle.orientation_coefficients`
  - yaw `0` entry loads `emagls_32kHz_dft_aligned_ypr_0_0_0.npy`
  - yaw `90` entry loads `emagls_32kHz_dft_aligned_ypr_90_0_0.npy`
- `select_orientation_coefficients(front_end_bundle, yaw_deg=...)`
  - exact yaw lookup
  - raises a clear error if no coefficient entry exists
- Default `front_end_bundle.c_magls` remains yaw `0` for backward compatibility.
- Rotation-specific validation and listening now use the selected orientation-bank entry.

Validation:

- `diagnose-emagls --yaw-deg 90`:
  - selected project yaw `90` vs saved yaw `90`: `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`
- `audit --indent 2` artifact:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/`
  - yaw `0` direct parity: pass
  - yaw `90` direct parity with selected bank entry: pass
  - only remaining audit blocker: `human_listening`
- `rotation_90__project_bsm_magls.wav` is now generated from `project_bsm_magls_yaw_90`, not static yaw `0`.

Important scope note:

- The implemented bank currently uses the available saved Array2Binaural aligned-ypr eMagLS references for yaw `0` and yaw `90`.
- The Berebi-style BSM-iMagLS requirement remains the next coefficient-generation step:
  - each supported orientation should also receive a DNN-solver-optimized BSM-iMagLS coefficient entry once the iMagLS objective/export path is implemented.

## Required Outcome

- `front_end_bundle.c_magls[f, m, e]` must be Array2Binaural eMagLS-compatible, not merely shape-compatible.
- `residual_solver.build_solver_input_pack(...).c_magls` and the packed `c_magls_*` channels must use that same coefficient object.
- `c_ls`, `c_magls`, and `c_magls - c_ls` must be generated from a consistent front-end parameterization. Do not combine a repaired Array2Binaural `c_magls` with the old project-side `c_ls` if their LS/MagLS source semantics differ.
- The coefficient parity gate must pass for the saved yaw `0` reference before any neural-network training starts.
- Yaw `90` parity should also pass if the implementation supports saved-reference rotations in this task; otherwise it must be left as an explicit remaining rotation-generalization blocker.

## Current Evidence

- Saved reference file:
  - `07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/emagls_32kHz_dft_aligned_ypr_0_0_0.npy`
  - shape `(5, 2, 513)`, interpreted by `evaluate_ilds_itds.py` as `[microphone, ear, frequency]`
- Project canonical coefficient shape:
  - `front_end_bundle.c_magls.shape == (513, 5, 2)`
- Existing canonicalization is correct as an axis transform:
  - `bsm/phase02/correctness_validation.py` transposes `(5, 2, 513)` to `(513, 5, 2)`
- Existing parity result after canonicalization:
  - yaw `0`: `max_abs = 3.333735227584839`, `mean_abs = 0.3605842888355255`, `nmse = 6.4899373054504395`
  - yaw `90`: `max_abs = 3.1904966831207275`, `mean_abs = 0.37621447443962097`, `nmse = 5.828028678894043`
- Energy probe on 2026-04-21:
  - project `c_magls` mean energy: `0.22261136770248413`
  - saved yaw `0` mean energy: `0.0397939458489418`
  - saved yaw `90` mean energy: `0.04525383561849594`
- Simple explanations have effectively been ruled out:
  - global scalar fit, conjugation, ear swap, and best microphone permutation all leave yaw `0` scalar-fit NMSE near `1.0`
  - this is not an axis-only or one-scalar-gain problem.

## Problem Location

The parity failure is caused by a coefficient-contract mismatch, not by a simple implementation typo in the final axis order.

There are two distinct coefficient objects currently being conflated:

- Project `front_end_bundle.c_magls` is a project-side raw-like eMagLS solve:
  - solved directly at `32000 Hz`
  - `fft_size = 1024`
  - array delay `22` samples
  - HRTF delay `91` samples after 32 kHz resampling
  - no visible Array2Binaural aligned-ypr postprocess
- Saved `emagls_32kHz_dft_aligned_ypr_0_0_0.npy` is an opaque Array2Binaural aligned-ypr reference/runtime artifact:
  - shape `[microphone, ear, frequency]`
  - consumed by `evaluate_ilds_itds.py`
  - not produced by the visible `compute_emagls2_for_rotations.py` save statements
  - not reproduced by the visible raw eMagLS output or by the visible roll/cut/window postprocess tested on 2026-04-21

The huge TASK-0007 parity failure comes primarily from comparing those two different coefficient semantics as if they were the same tensor.

Diagnostic facts:

- A direct port of visible `compute_emagls2_for_rotations.py` for yaw `0`, using `48000 Hz`, `NFFT = 1536`, HRTF delay `139`, mic delay `33`, and exporting the first `513` raw bins, produced:
  - generated raw energy `0.23695190250873566`
  - saved aligned-ypr energy `0.0397939458489418`
  - raw-vs-saved `max_abs = 3.2770965099334717`
  - raw-vs-saved `mean_abs = 0.3734230697154999`
  - raw-vs-saved `nmse = 6.843871593475342`
- The same raw visible-Array2Binaural port is much closer to project `c_magls` than to the saved aligned-ypr file:
  - project energy `0.22261136770248413`
  - project-vs-raw `mean_abs = 0.21994052827358246`
  - project-vs-raw `nmse = 0.47708389163017273`
  - project-vs-raw magnitude mean absolute difference `0.04673570767045021`
  - project-vs-saved magnitude mean absolute difference `0.27886465191841125`
- Applying the visible Array2Binaural time-domain postprocess from `compute_emagls2_for_rotations.py` did not reproduce the saved aligned-ypr file:
  - raw first `513` bins: `nmse = 6.843871593475342`
  - roll/cut/window/1024-FFT with `FILTLEN = 768`: `nmse = 4.8824052810668945`
  - small search over `FILTLEN in {256, 384, 512, 640, 768, 1024, 1536}`, roll/no-roll, Tukey/rectangular windows, and integer phase shifts did not find a matching transform
- Therefore, `emagls_32kHz_dft_aligned_ypr_*` has missing provenance in the checked-in Array2Binaural tree. It is not safe to treat it as the visible raw eMagLS solver output.

Secondary issue:

- Project `c_magls` is still not an exact Array2Binaural raw eMagLS coefficient either, because the project solves directly at 32 kHz/1024 while visible Array2Binaural solves at 48 kHz/1536 before exporting 32 kHz-range bins.
- That secondary mismatch is smaller than the aligned-ypr mismatch but still matters if the accepted neural-network input is defined as raw Array2Binaural eMagLS.

Precise conclusion:

- The blocker is a broken parity contract: `correctness_validation` compares project raw-like `c_magls` against an opaque saved aligned-ypr coefficient artifact.
- The next session must first decide and encode the authoritative NN input coefficient semantics:
  - if NN input should match saved Array2Binaural aligned-ypr runtime filters, `front_end_bundle.c_magls` must load or faithfully regenerate `emagls_32kHz_dft_aligned_ypr_*`;
  - if NN input should match visible raw Array2Binaural eMagLS solver coefficients, TASK-0007 must stop using `emagls_32kHz_dft_aligned_ypr_*` as the direct coefficient parity authority and must generate a raw reference instead.
- The project cannot honestly pass TASK-0007 by only transposing axes or tuning tolerance.

## Source Reading Findings

### Project Implementation

- `bsm/phase02/front_end_bundle.py` currently builds HRTF SH responses directly at `sample_rate_hz=32000`, `fft_size=1024`.
- `_phase_aligned_hrtf_sh` resamples KU100 from `44100` to `32000`, finds delay `91`, applies a positive phase advance, then returns `513` bins.
- `_phase_aligned_steering_response` loads the 32 kHz Easycom SH IR directly, uses mic delay `22`, and returns `513` bins.
- `_solve_magls_coefficients` performs a low-frequency LS branch and a high-frequency phase-recursive MagLS branch, then applies monaural diffuse-field equalization.
- The project equation structure resembles Array2Binaural, but the parameterization differs before the solve starts.

### Array2Binaural Reference Implementation

- `compute_emagls2_for_rotations.py` computes filters at `FS = 48000`, `NFFT = 1536`.
- It resamples KU100 from `44100` to `48000`, finds HRTF delay `139`, and applies the delay phase in the HRTF SH frequency domain.
- It loads `Easycom_array_32000Hz_o25_22samps_delay.npy`, resamples the array IR from `32000` to `48000` with scale `FS_ARRAY / FS`, and uses mic delay `int(22 * 48000 / 32000) == 33`.
- It solves on `spaudiopy.grids.load_n_design(35)` and computes `regInvY` once from the global design-grid steering tensor.
- It rotates the HRTF SH target with `calculate_rotation_matrix(5, yaw, pitch, roll)`, then solves ear-specific filters:
  - LS below `f_cut = 2000`
  - phase-recursive MagLS above `2000`
  - monaural diffuse-field equalization from target and estimated response covariance
- It saves `filters_32kHz_dft.npy` as the first `513` bins of the 48 kHz, `1536`-point frequency-domain filters.
- The checked-in `emagls_32kHz_dft_aligned_ypr_0_0_0.npy` and `..._90_0_0.npy` are consumed by `evaluate_ilds_itds.py`, but the exact script that produced these aligned `ypr` files is not present. Treat these files as the current TASK-0007 saved-reference artifact, not as proven output of the visible raw compute script.

### Evaluation-Side Semantics

- `evaluate_ilds_itds.py` loads the saved `emagls_32kHz_dft_aligned_ypr_%d_0_0.npy` files and renders them as:
  - `Hl_emagls_f = sum(rot_filter[:, 0, None, :].T * Df, -1)`
  - `Hr_emagls_f = sum(rot_filter[:, 1, None, :].T * Df, -1)`
- This confirms saved filter axes are `[microphone, ear, frequency]`.
- The same file contains a commented phase-ramp hint near the eMagLS load:
  - `rot_filter *= exp(-1j * 2*pi*fvec*139/48000)`
- That hint is important because the saved `aligned_ypr` files may already include a phase alignment or de-alignment step that is not represented in the current project solver.

## Paper Constraints To Preserve

- Madmoni et al. 2025 formulate BSM as minimizing an expected binaural signal error over the sound field, not as solving one spatial point.
- Under simplifying assumptions, the BSM LS solution is a global direction-set fit of array steering vectors to HRTFs with regularization.
- BSM-MagLS replaces the high-frequency complex matching objective with magnitude matching, while retaining complex LS below a cutoff frequency.
- Head rotation compensation is represented by modifying the HRTF vector or steering vectors according to the rotation, not by evaluating a single direction.
- Berebi et al. 2025 do consider head rotation:
  - the stated contributions include a head-rotation compensation analysis
  - Section V-D3 evaluates performance under head rotation compensation
  - the listening experiment precomputes BSM coefficients for each head orientation and selects them from head-tracker readings
  - therefore iMagLS is not a static-only paper; however, its core yaw/pitch/roll coefficient-generation contract remains separate from this task's saved aligned-ypr yaw `0` repair.
- The Array2Binaural paper represented by `E-library page.pdf` states the same end-to-end MLS idea: solve on a fine grid of directions, use phase continuation above cutoff, and apply monaural diffuse-field equalization.
- Therefore, any repair that computes `c_magls` from a single evaluation azimuth is invalid. The repaired implementation must solve over the global optimization grid.

## Root Cause

Root cause:

- `TASK-0007` uses the wrong direct-parity assumption.
- It assumes saved `emagls_32kHz_dft_aligned_ypr_*` and project `front_end_bundle.c_magls` are the same semantic coefficient object after axis canonicalization.
- They are not.

Contributing cause:

- Project `front_end_bundle.c_magls` was implemented as an independent 32 kHz eMagLS-like solver, not as a faithful wrapper around either:
  - saved Array2Binaural aligned-ypr files, or
  - visible Array2Binaural 48 kHz raw eMagLS generation.

Not root causes:

- Axis order alone.
- Ear swap.
- Microphone permutation.
- Global complex scalar or gain.
- A single-point spatial solve. The project code and visible Array2Binaural code both solve over the global optimization grid; the issue is which coefficient artifact and parameterization are being compared.

## Implementation Plan

### Phase 0. Preserve The Located Failure

- Keep the existing `TASK-0007/20260420T083829Z` artifacts as the failing baseline.
- Add or extend a diagnostic CLI that reports the already-located distinction explicitly:
  - source reference shape and hash
  - canonical reference shape
  - project `c_ls` and `c_magls` energy
  - saved-reference energy
  - banded parity metrics
  - best scalar/conjugation/ear-swap/mic-permutation probes
  - visible raw Array2Binaural-port metrics when available
  - aligned-ypr postprocess search metrics when available
- Suggested command:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation diagnose-emagls --yaw-deg 0 --indent 2
```

If adding this subcommand to `correctness_validation.py` makes the module too large, place the heavy logic in a new `bsm.phase02.array2binaural_emagls` module and call it from the validation harness.

The diagnostic CLI should not merely say "mismatch"; it must distinguish:

- project raw-like 32 kHz eMagLS
- visible Array2Binaural raw 48 kHz eMagLS
- saved Array2Binaural aligned-ypr artifact

### Phase 1. Build A Reference-Faithful eMagLS Module

Create `bsm/phase02/array2binaural_emagls.py` with pure project-side wrappers around the Array2Binaural algorithm and saved references. The module must be deterministic and testable without editing the imported reference tree.

Required public functions:

- `load_saved_aligned_ypr_emagls_reference(repo_root, yaw_deg) -> coefficients[f, m, e]`
- `build_visible_raw_array2binaural_emagls_coefficients(repo_root, yaw_deg=0, pitch_deg=0, roll_deg=0) -> EmaglsBuildResult`
- `compare_emagls_to_saved_reference(result, saved_reference) -> metrics`

Required build constants:

- `compute_sample_rate_hz = 48000`
- `array_source_sample_rate_hz = 32000`
- `nfft = 1536`
- `export_frequency_bins = 513`
- `array_delay_samples_32k = 22`
- `array_delay_samples_48k = 33`
- `hrtf_order = 5`
- `array_order = 25`
- `optimization_grid = spaudiopy.grids.load_n_design(35)`
- `frequency_cut_hz = 2000`
- diagonal loading factor `0.001 * largest_eigenvalue`

Algorithm details to mirror exactly:

- Load KU100 `irsOrd5.wav`.
- Resample to 48 kHz using `signal.resample_poly(hrir, 48000, fs_hrirs, axis=0) * fs_hrirs / 48000`.
- Apply the right-ear SH sign convention from Array2Binaural.
- Compute `dl_sh5`, `dr_sh5` with `np.fft.rfft(..., 1536)` and the HRTF delay phase.
- Load Easycom SH IR at 32 kHz.
- Resample to 48 kHz using `32000 / 48000 * signal.resample_poly(ir_sh, 48000, 32000, axis=0)`.
- Decode array steering on `load_n_design(35)` using order `25`.
- Compute `d = rfft(optim_irs, 1536, axis=0)` and apply mic-delay phase at 48 kHz.
- Compute global `regInvY = inv(conj(d).T @ d + loading) @ conj(d).T`.
- For exact yaw/pitch/roll, compute `rotmat_o5 = calculate_rotation_matrix(5, yaw, pitch, roll)`.
- Rotate the HRTF SH target exactly as Array2Binaural does.
- For each frequency:
  - below or equal to `2000 Hz`, use complex LS
  - above `2000 Hz`, take phase from previous reconstructed response and solve the magnitude target
  - stop or ignore bins above `16000 Hz`; export only bins `0:513`
- Apply monaural diffuse-field equalization after the full frequency recursion.
- Return canonical `[frequency, microphone, ear]` complex64 coefficients and metadata.

### Phase 2. Choose And Encode The Coefficient Authority

Do not assume a single reference silently. The implementation must make one explicit authority choice and document it in code and artifacts.

Option A: saved aligned-ypr is the neural-network input authority.

- `front_end_bundle.c_magls` should load `emagls_32kHz_dft_aligned_ypr_0_0_0.npy` for the yaw `0` static default, after canonicalization.
- The implementation must explain that this is an opaque Array2Binaural aligned-ypr artifact whose exact generation script is absent.
- The project must not claim it has regenerated the aligned-ypr coefficients unless a reproducing transform is found.
- `c_ls` must be made compatible or explicitly marked as a different baseline source.

Option B: visible raw Array2Binaural eMagLS is the neural-network input authority.

- `front_end_bundle.c_magls` should be generated by the visible 48 kHz/1536 Array2Binaural raw path.
- TASK-0007 coefficient parity must compare against a generated raw reference, not the saved aligned-ypr file.
- Saved aligned-ypr files should remain renderer/listening reference artifacts, not direct coefficient parity authority.

Given the user's requirement that the NN input filters should match Array2Binaural eMagLS parameters, Option A is the conservative interpretation if the saved aligned-ypr files are the actual filters used by the Array2Binaural evaluation/runtime path. Option B is acceptable only if the project explicitly defines "parameters" as visible raw solver coefficients and records why aligned-ypr is excluded from coefficient parity.

### Phase 3. Integrate The Repaired Coefficients

- Update `bsm.phase02.front_end_bundle` so the default `c_magls` comes from the reference-faithful Array2Binaural eMagLS path.
- Rebuild `c_ls` from the same steering/HRTF parameterization or store explicit metadata proving it is compatible with the repaired `c_magls`.
- Add metadata to `FrontEndBundle.to_summary()`:
  - `c_ls_source`
  - `c_magls_source`
  - `emagls_compute_sample_rate_hz`
  - `emagls_nfft`
  - `emagls_reference_yaw_deg`
  - `emagls_reference_path` when a saved file is used
- Keep public shapes unchanged:
  - `V[d, f, m] == (72, 513, 5)`
  - `h[d, f, e] == (72, 513, 2)`
  - `c_ls[f, m, e] == (513, 5, 2)`
  - `c_magls[f, m, e] == (513, 5, 2)`
- Do not change the residual solver architecture in this task unless a metadata field is needed for traceability.

### Phase 4. Re-run Gates And Artifacts

Run:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation audit --indent 2
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

Expected artifact updates:

- new `06_Assets/Generated_Artifacts/TASK-0007/<timestamp>/parity_metrics.json`
- new `validation_summary.json` with coefficient parity passing
- new `render_metrics.json` and `cue_metrics.json` after coefficient repair
- new listening WAVs if rendered output changes materially

## Test Requirements

Add focused tests before relying on the fix:

- `test_load_saved_emagls_reference_axes`
  - saved `(5, 2, 513)` becomes `(513, 5, 2)`
- `test_visible_raw_array2binaural_emagls_yaw0_is_distinguished_from_saved_aligned_ypr`
  - generated visible raw yaw `0` and saved aligned-ypr yaw `0` are reported as different coefficient semantics unless a reproducing aligned-ypr transform is implemented
- `test_selected_authority_yaw0_parity`
  - if Option A is selected, `front_end_bundle.c_magls` matches saved aligned-ypr yaw `0`
  - if Option B is selected, `front_end_bundle.c_magls` matches generated visible raw yaw `0`, and saved aligned-ypr is excluded from direct coefficient parity with an explicit artifact note
- `test_front_end_bundle_uses_array2binaural_magls_source`
  - `bundle.c_magls` equals the repaired yaw `0` coefficient source
  - summary metadata records the source
- `test_solver_input_pack_uses_repaired_c_magls`
  - packed `c_magls_*` channels reconstruct the repaired complex coefficient values
- `test_renderer_accepts_saved_reference_coefficients`
  - saved reference renders through project renderer without shape or finite errors

If the exact-ypr generator is too slow for the default unit suite, mark the heavy parity test with a fast fixture or cache a generated diagnostic artifact. The normal discovered tests must still exercise the loader, metadata, and solver input contract.

## Acceptance Criteria

- yaw `0` coefficient parity passes against the explicitly selected authority:
  - Option A: saved aligned-ypr Array2Binaural reference
  - Option B: generated visible raw Array2Binaural eMagLS reference
- The validation summary no longer lists `coefficient_parity` as a blocker.
- `front_end_bundle.c_magls` is the same coefficient object used by `residual_solver.build_solver_input_pack`.
- `c_magls` source metadata is visible in JSON summaries and test assertions.
- Full unit tests pass.
- Residual solver smoke still runs with finite loss and exports TASK-0006-style artifacts.
- If human listening remains pending, training may still be blocked by `human_listening`, but not by coefficient parity.

## Stop Conditions

Stop and document instead of forcing a partial fix if:

- the saved `aligned_ypr` files cannot be reproduced from the visible Array2Binaural code plus a clearly documented phase/time alignment step;
- Option A is selected by directly loading saved yaw `0`, but the next required experiment needs generated yaw/pitch/roll filters whose aligned-ypr provenance is still unavailable;
- repairing `c_magls` reveals that current `V` or `h` semantics are inconsistent with Array2Binaural evaluation, requiring a larger front-end contract revision.

In those cases, write the narrowed cause into `TASK-0007`, keep `training_allowed = false`, and propose the smallest next task.
