---
Document_ID: EXP-0002
Title: Pre-Training Correctness Validation
Status: Draft
Phase: Phase_02_Development
Track: Experiment
Maturity: Exploration
Related_Docs:
  - 04_Tasks/Active/TASK-0007_Pre_Training_Correctness_Validation.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0008_Pre_Training_Correctness_Validation.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 05_Experiments/Registry/EXP-Registry.md
  - 06_Assets/Generated_Artifacts/Index.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# Pre-Training Correctness Validation

## Purpose

- Define the repeatable experiment protocol for `TASK-0007`.
- Verify numerical correctness and generate listening evidence before real neural-network training.
- Keep the protocol separate from the implementation session so later reruns can reuse the same checks.

## Required Runtime

```bash
conda activate bsm_harness_py311
```

Or run every command through:

```bash
conda run -n bsm_harness_py311 <command>
```

## Execution Protocol

1. Run the validation audit.

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation audit --indent 2
```

2. Run the full project-side regression suite.

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

3. Rerun the residual solver smoke gate.

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

4. Record all outputs in `SESSION-P2-0008`.

## Artifact Layout

Use exactly one timestamped directory per audit run:

```text
06_Assets/Generated_Artifacts/TASK-0007/<YYYYMMDDTHHMMSSZ>/
  validation_summary.json
  parity_metrics.json
  render_metrics.json
  cue_metrics.json
  audio_manifest.json
  listening_notes.md
  audio/
    *.wav
```

## Listening Protocol

- Use headphones.
- Keep system enhancement or spatialization effects disabled.
- Listen at a comfortable fixed level.
- Compare the target, project BSM-MagLS, Array2Binaural reference, and repaired project output when available.
- Latest listening files:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/audio/`
- Fill the notes table at:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/listening_notes.md`
- Required checks:
  - channel swap
  - gross coloration
  - image direction
  - unstable ITD
  - level imbalance
  - clipping or crackle
  - obvious artifacts

## Listening Notes Template

```markdown
# TASK-0007 Listening Notes

Artifact directory: `06_Assets/Generated_Artifacts/TASK-0007/<timestamp>/`
Listener:
Date:
Playback device:

| Case | File | Channel Swap | Direction Plausible | Coloration | ITD Stability | Level Balance | Clipping/Artifacts | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| frontal |  |  |  |  |  |  |  |  |
| lateral_left |  |  |  |  |  |  |  |  |
| lateral_right |  |  |  |  |  |  |  |  |
| rear |  |  |  |  |  |  |  |  |
| rotation_90 |  |  |  |  |  |  |  |  |
```

## Acceptance

- The experiment is successful only if:
  - validation audit exits successfully
  - regression suite passes
  - residual solver smoke passes
  - all required JSON artifact files exist
  - audio files exist and are listed in `audio_manifest.json`
  - `listening_notes.md` is filled
- If any required item fails:
  - keep `TASK-0007` active or move it to blocked
  - record the exact blocker in `SESSION-P2-0008`
  - do not start real training.

## Latest Result

### 2026-04-21 Machine-Gate Rerun After TASK-0007A Repair

Artifact directory:

```text
06_Assets/Generated_Artifacts/TASK-0007/20260421T053758Z/
```

Coefficient authority:

- saved Array2Binaural aligned-ypr yaw `0` runtime filters
- source file:
  - `07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/emagls_32kHz_dft_aligned_ypr_0_0_0.npy`
- canonical project shape:
  - `[frequency, microphone, ear] == (513, 5, 2)`

Gate result:

- `environment_and_assets = true`
- `coefficient_parity = true`
- `renderer_parity = true`
- `cue_bank = true`
- `solver_export_readiness = true`
- `listening_audio = true`
- `human_listening = false`

Coefficient parity:

- yaw `0` saved aligned-ypr reference:
  - `max_abs = 0.0`
  - `mean_abs = 0.0`
  - `nmse = 0.0`
- yaw `90`:
  - not supported in this first yaw `0` repair artifact
  - superseded by the later orientation-bank listening set below

Regression:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

- `27` tests passed.

Residual solver smoke:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

- `ok = true`
- finite metrics and export artifacts present
- `loss_reduced = false` is reported but not blocking because `c_ls == c_magls` under the saved aligned-ypr coefficient authority.

Current experiment status:

- The coefficient parity blocker is repaired.
- Real training remains disallowed until the human-listening gate is completed.

## Future Orientation Coefficient Experiment Direction

- The project will follow the Berebi et al. 2025 head-tracked BSM-iMagLS approach:
  - precompute one coefficient set for each supported head orientation
  - generate each BSM-iMagLS coefficient set through the DNN-based solver for that orientation
  - save those coefficients in an orientation-indexed bank
  - select the correct coefficient set from head-tracker yaw/pitch/roll state during playback/inference
- This experiment does not close that rotation-generalization work.
- The current experiment only repairs and validates the saved aligned-ypr yaw `0` coefficient authority.

## Latest Orientation-Bank Listening Set

### 2026-04-21 yaw `90` Selection Repair

Artifact directory:

```text
06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/
```

What changed:

- `front_end_bundle` now exposes an orientation coefficient bank with yaw `0` and yaw `90`.
- `rotation_90__project_bsm_magls.wav` is generated from `project_bsm_magls_yaw_90`.
- `rotation_90__array2binaural_emagls_reference.wav` is generated from `array2binaural_emagls_reference_yaw_90`.
- Both are now the same saved aligned-ypr yaw `90` coefficient object under the current eMagLS authority.

Expected listening result:

- Non-rotation cases:
  - `project_bsm_magls` and `array2binaural_emagls_reference` should remain very close or identical.
- `rotation_90` case:
  - `project_bsm_magls` and `array2binaural_emagls_reference` should now also be very close or identical.
  - Any remaining obvious difference should be treated as a new bug in selection, rendering, or artifact generation.

Machine result:

- yaw `0` selected-bank parity: `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`
- yaw `90` selected-bank parity: `max_abs = 0.0`, `mean_abs = 0.0`, `nmse = 0.0`
- `28` tests passed.

Scope note:

- This closes yaw `90` selection for the saved eMagLS orientation bank.
- It does not yet implement Berebi-style DNN-solver-optimized BSM-iMagLS coefficients per orientation.
