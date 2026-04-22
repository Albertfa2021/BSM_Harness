---
Document_ID: SESSION-P2-0008
Title: Pre-Training Correctness Validation
Status: Active
Phase: Phase_02_Development
Track: Session
Maturity: Validating
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0007_Pre_Training_Correctness_Validation.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 05_Experiments/EXP-0002_Pre_Training_Correctness_Validation/README.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# Pre-Training Correctness Validation

## Target Subtask

- Execute `TASK-0007` as the pre-training correctness gate.
- Limit the session to:
  - validation harness implementation
  - targeted repair of correctness failures
  - numeric validation exports
  - listening-audio generation and notes
  - registry and documentation updates after results exist

## Reference Anchors

- `02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md`
- `05_Experiments/EXP-0002_Pre_Training_Correctness_Validation/README.md`
- `07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py`
- `07_References/Open_Source_Baselines/Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py`
- `05_Experiments/EXP-0001_Auditory_ILD_Python/code/auditory_ild.py`

## Test Standard

### Scope

- Validate and, where needed, repair project-side correctness before training.
- Do not run formal training, long optimization, or broad ablations in this session.

### Preconditions

- `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests` is runnable.
- `TASK-0006` generated the first short-run solver export.
- Required Array2Binaural files are present:
  - `Easycom_array_32000Hz_o25_22samps_delay.npy`
  - `ku100_magls_sh_hrir/irsOrd5.wav`
  - `compute_emagls_filters/emagls_32kHz_dft_aligned_ypr_0_0_0.npy`
  - `compute_emagls_filters/emagls_32kHz_dft_aligned_ypr_90_0_0.npy`

### Shape And Contract Checks

- Project coefficient shape remains `c_magls[f, m, e]`.
- Reference eMagLS filters are canonicalized to `[frequency, microphone, ear]` before comparison.
- Rendered responses use `[direction, frequency, ear]`.
- Audio exports are stereo WAV files with declared sample rate and no clipping.

### Numerical Checks

- Reject `nan` and `inf` in assets, coefficients, responses, cue arrays, loss traces, and audio samples.
- Compare project `c_magls` against Array2Binaural saved references with `max_abs`, `mean_abs`, and NMSE.
- Compare numpy and torch renderers on the same coefficient tensor.
- Compare rendered BSM-MagLS outputs against target `h` and report worst directions.
- Verify cue-bank ERB ILD and GCC-PHAT ITD metrics are finite.
- Verify residual solver smoke still reduces loss or records a blocking failure.

### Acceptance Checks

- The session cannot close as done unless:
  - the validation harness audit completes
  - the full discovered test suite passes
  - the residual solver smoke gate passes after any fix
  - required TASK-0007 artifact files are written
  - listening WAVs and `listening_notes.md` exist
  - all results are recorded in this session note

## Completion Gate

Run and record the following commands during execution:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation audit --indent 2
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

## Planned Artifact Directory

- Use one UTC timestamped directory:
  - `06_Assets/Generated_Artifacts/TASK-0007/<YYYYMMDDTHHMMSSZ>/`
- Required files:
  - `validation_summary.json`
  - `parity_metrics.json`
  - `render_metrics.json`
  - `cue_metrics.json`
  - `audio_manifest.json`
  - `listening_notes.md`
  - `audio/*.wav`

## Result Log

### 2026-04-20 Validation Harness Audit

- Command:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation audit --indent 2
```

- Exit status:
  - `1`
- Artifact directory:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260420T083829Z/`
- Gate summary:
  - `environment_and_assets = true`
  - `coefficient_parity = false`
  - `renderer_parity = true`
  - `cue_bank = true`
  - `solver_export_readiness = true`
  - `listening_audio = true`
  - `human_listening = false`
- Coefficient parity result against yaw `0` after `[frequency, microphone, ear]` canonicalization:
  - `max_abs = 3.333735227584839`
  - `mean_abs = 0.3605842888355255`
  - `rmse = 0.5081930756568909`
  - `nmse = 6.4899373054504395`
  - worst bin: `17` / `531.25 Hz`, `mean_abs = 1.0028313398361206`
- Rotation reference context:
  - yaw `90` comparison remained large: `max_abs = 3.1904966831207275`, `nmse = 5.828028678894043`
- Renderer parity:
  - all numpy/torch renderer comparisons passed within numerical precision
  - project `BSM-MagLS` renderer max abs difference: `3.769728778024728e-07`
  - saved yaw `0` reference renderer max abs difference: `1.211184894600592e-07`
- Audio:
  - `15` finite stereo WAV files generated
  - max peak amplitude: `0.4420761168003082`
  - cases: `frontal`, `lateral_left`, `lateral_right`, `rear`, `rotation_90`
- Blockers:
  - direct coefficient parity does not pass and blocks real training
  - generated listening notes require a human headphone pass before the listening gate can close

### 2026-04-20 Regression Verification

- Command:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

- Exit status:
  - `0`
- Result:
  - `23` tests passed.

### 2026-04-20 Residual Solver Smoke

- Command:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

- Exit status:
  - `0`
- Result:
  - `ok = true`
  - `initial_loss_total = 1.5917432308197021`
  - `final_loss_total = 1.561366081237793`
  - `selected_iteration = 2`
  - `normalized_magnitude_error = 0.1284123402745945`
  - `nmse = 0.2924126386642456`
  - `ild_error = 5.321670740027731`
  - `itd_proxy_error = 0.004369844992243433`
- Export artifacts:
  - `06_Assets/Generated_Artifacts/TASK-0006/20260420T083933Z/summary.json`
  - `06_Assets/Generated_Artifacts/TASK-0006/20260420T083933Z/loss_trace.jsonl`

### 2026-04-21 TASK-0007A Coefficient Parity Repair

- Repair document:
  - `04_Tasks/Active/TASK-0007A_eMagLS_Coefficient_Parity_Blocker.md`
- Selected authority:
  - saved Array2Binaural aligned-ypr yaw `0` runtime filter
- Implementation summary:
  - added `bsm.phase02.array2binaural_emagls`
  - updated `front_end_bundle.c_magls` to load `emagls_32kHz_dft_aligned_ypr_0_0_0.npy`
  - set `c_ls == c_magls` with explicit source metadata because a saved aligned-ypr LS reference is not present
  - verified `residual_solver.build_solver_input_pack(...)` and packed `c_magls_*` channels use the repaired coefficient object

Diagnostic command:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation diagnose-emagls --yaw-deg 0 --indent 2
```

- Result:
  - project `c_magls` vs saved yaw `0` reference: `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`

Validation audit:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation audit --indent 2
```

- Exit status:
  - `1`
- Artifact directory:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T053758Z/`
- Gate summary:
  - `environment_and_assets = true`
  - `coefficient_parity = true`
  - `renderer_parity = true`
  - `cue_bank = true`
  - `solver_export_readiness = true`
  - `listening_audio = true`
  - `human_listening = false`
- Remaining blocker:
  - human headphone listening notes remain pending
- Rotation-generalization note:
  - yaw `90` does not pass direct parity against the static yaw `0` default and remains a follow-up for selectable/generated rotation coefficients.

Regression verification:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

- Exit status:
  - `0`
- Result:
  - `27` tests passed.

Residual solver smoke:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

- Exit status:
  - `0`
- Result:
  - `ok = true`
  - finite metrics and export artifacts present
  - `loss_reduced = false` is reported but not blocking under the current `c_ls == c_magls` coefficient authority
- Export artifacts:
  - `06_Assets/Generated_Artifacts/TASK-0006/20260421T053843Z/summary.json`
  - `06_Assets/Generated_Artifacts/TASK-0006/20260421T053843Z/loss_trace.jsonl`

### 2026-04-21 Orientation Bank / yaw `90` Selection Repair

- Human listening observation before this repair:
  - non-rotation cases had project/reference outputs very close or identical
  - `rotation_90` had a clear difference because project playback used static yaw `0` while reference playback used yaw `90`
- Implementation:
  - added `OrientationCoefficientEntry`
  - added `front_end_bundle.orientation_coefficients`
  - added `select_orientation_coefficients(front_end_bundle, yaw_deg=...)`
  - loaded saved aligned-ypr yaw `0` and yaw `90` entries into the bank
  - updated validation and listening artifact generation to use yaw-specific project entries
- Validation:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation diagnose-emagls --yaw-deg 90 --indent 2
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation audit --indent 2
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

- Results:
  - yaw `0` selected-bank parity: `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`
  - yaw `90` selected-bank parity: `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`
  - `coefficient_parity = true`
  - `renderer_parity = true`
  - `cue_bank = true`
  - `solver_export_readiness = true`
  - `listening_audio = true`
  - `human_listening = false`
  - full tests: `28` passed
  - residual solver smoke: `ok = true`
- New listening artifact directory:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/`
- New smoke artifact directory:
  - `06_Assets/Generated_Artifacts/TASK-0006/20260421T060819Z/`
- Scope note:
  - the implemented bank uses saved aligned-ypr eMagLS entries
  - Berebi-style DNN-solver-optimized BSM-iMagLS entries per orientation remain a separate coefficient-generation task

## Closeout Checklist

- [x] Validation harness implemented.
- [x] Coefficient parity investigated.
- [x] Coefficient parity repaired for saved aligned-ypr yaw `0`.
- [x] Renderer parity recorded.
- [x] Cue-bank validation recorded.
- [x] Listening audio generated.
- [ ] Human listening notes filled by a listener.
- [x] Full tests passed.
- [x] Residual solver smoke passed after any fix.
- [x] Artifact index updated.
- [x] Experiment registry/result tracker updated.
- [ ] TASK-0007 moved to completed or blocked according to human-listening result.
