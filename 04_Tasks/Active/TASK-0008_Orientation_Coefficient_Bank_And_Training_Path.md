---
Document_ID: TASK-0008
Title: Orientation Coefficient Bank And Training Path
Status: Active
Phase: Phase_02_Development
Track: Task
Maturity: Validating
Related_Docs:
  - 04_Tasks/Active/TASK-0007_Pre_Training_Correctness_Validation.md
  - 04_Tasks/Active/TASK-0007A_eMagLS_Coefficient_Parity_Blocker.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0008_Pre_Training_Correctness_Validation.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0009_Orientation_Training_Path_Smoke.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 02_Architecture/Data/ARCH-03_Data_Schema.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md
  - 05_Experiments/EXP-0002_Pre_Training_Correctness_Validation/README.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py
  - 07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/emagls_32kHz_dft_aligned_ypr_0_0_0.npy
  - 07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/emagls_32kHz_dft_aligned_ypr_90_0_0.npy
  - 07_References/Papers/Berebi 等 - 2025 - BSM-iMagLS ILD Informed Binaural Signal Matching for Reproduction with Head-Mounted Microphone Arra.pdf
  - 07_References/Papers/Madmoni 等 - 2025 - Design and Analysis of Binaural Signal Matching with Arbitrary Microphone Arrays and Listener Head R.pdf
Last_Updated: 2026-04-21
Review_Required: Yes
---

# Orientation Coefficient Bank And Training Path

## Purpose

`TASK-0008` turns the `TASK-0007` orientation repair into a formal training-path preparation task.

The task has two equal responsibilities:

- make the orientation coefficient bank a deliberate, documented, reusable interface instead of a one-off yaw `90` validation fix
- define the neural-network training path clearly enough that the next implementation session can wire and validate it without redesigning the route

This task does not run the large optimization campaign. Large planned runs, long logs, checkpointing, ablations, and comparative optimization schedules belong to `TASK-0009`.

`TASK-0008` still must validate short-run optimization quality. The distinction is:

- `TASK-0008`: orientation-aware short-run quality validation that proves the route is not merely finite, but also capable of producing a meaningful optimization result at smoke scale
- `TASK-0009`: planned large-scale optimization with detailed logging, run matrices, checkpoints, and comparative campaigns

## Starting Point From TASK-0007

`TASK-0007` established the following facts:

- Static yaw `0` cannot represent all head rotations.
- Saved Array2Binaural aligned-ypr eMagLS filters are the current coefficient authority for the repaired static default.
- The project has two available saved orientation entries:
  - yaw `0`: `emagls_32kHz_dft_aligned_ypr_0_0_0.npy`
  - yaw `90`: `emagls_32kHz_dft_aligned_ypr_90_0_0.npy`
- `front_end_bundle.orientation_coefficients` currently exposes yaw `0` and yaw `90`.
- `select_orientation_coefficients(front_end_bundle, yaw_deg=...)` performs exact yaw lookup.
- Selected yaw `90` parity against the saved yaw `90` reference passes with zero error.
- The latest generated listening files are under:
  - `06_Assets/Generated_Artifacts/TASK-0007/20260421T060742Z/audio/`

`TASK-0008` must preserve these conclusions and convert them into a stable route for orientation-aware training preparation.

## Scope

### In Scope

- Formalize the orientation coefficient bank contract.
- Make the selected orientation entry the explicit coefficient source for any rotation-specific training-path smoke.
- Preserve legacy static callers by keeping `front_end_bundle.c_magls` as yaw `0`, while requiring rotation-specific callers to use the bank.
- Define how the neural solver consumes coefficients from a selected orientation.
- Define the minimum metadata and artifact schema needed before `TASK-0009`.
- Add smoke-scale validation for the route from selected orientation coefficients to solver input, joint coefficients, rendered response, loss breakdown, and export metadata.
- Validate short-run optimization quality for the selected orientation route.
- Update documentation so continuation by docs alone points to `TASK-0008` before any formal optimization campaign.

### Out Of Scope

- No large-scale neural-network optimization.
- No long training schedule.
- No checkpoint policy beyond naming the fields that `TASK-0009` must own.
- No ablation plan execution.
- No broad yaw grid beyond the currently available yaw `0` and yaw `90` saved references.
- No new claim that one global network generalizes across arbitrary HRTFs, ATFs, and head orientations.
- No online optimization during playback.
- No silent fallback from an unavailable yaw to static yaw `0`.

## Reference Or Authority

- Head-tracked coefficient-selection direction:
  - Berebi et al. 2025 BSM-iMagLS
  - Madmoni et al. 2025 head-rotation BSM formulation
- Local validation authority:
  - `TASK-0007`
  - `TASK-0007A`
  - `SESSION-P2-0008`
  - `ARCH-08` Gate 2A
- Training-path architecture:
  - `ARCH-07` Step G to Step J
  - `ARCH-03` canonical object names and axes
  - `ARCH-04` Contract 2A, Contract 4, Contract 5, Contract 6, Contract 7, and Contract 8
  - `ARCH-06` module boundaries

## Work Package 1. Orientation Coefficient Bank Contract

### Required Public Objects

- `OrientationCoefficientEntry`
- `FrontEndBundle.orientation_coefficients`
- `build_saved_aligned_ypr_orientation_bank(...)`
- `select_orientation_coefficients(front_end_bundle, yaw_deg=...)`

### Required Entry Semantics

Each orientation entry must represent one listener-head orientation and must record:

- `yaw_deg`
- `pitch_deg`
- `roll_deg`
- `c_ls[f, m, e]`
- `c_magls[f, m, e]`
- `c_ls_source`
- `c_magls_source`
- `coefficient_axis_semantics`
- `reference_path`, when loaded from a saved reference
- `reference_sha256`, when loaded from a saved reference

The canonical coefficient axis order remains:

```text
[frequency, microphone, ear]
```

### Required Selection Policy

- Selection is exact yaw lookup for the current task.
- yaw `0` must select the yaw `0` saved aligned-ypr entry.
- yaw `90` must select the yaw `90` saved aligned-ypr entry.
- Missing yaw entries must raise a clear error listing available yaw entries.
- No runtime code path may use static yaw `0` as a fallback for a requested head rotation.

### Current Coefficient Types

The current bank contains saved aligned-ypr eMagLS entries only:

- `c_ls`
  - compatibility baseline equal to `c_magls`
  - source must state that no saved aligned-ypr LS reference is present
- `c_magls`
  - saved Array2Binaural aligned-ypr runtime artifact

Future BSM-iMagLS entries are not part of the current coefficient authority. They must be added later as a distinct coefficient type, for example `c_imagls`, after the DNN-solver-generated coefficient export path exists.

## Work Package 2. Neural Training Path Definition

The task must define and validate the smoke-scale route below. This is the preparation route for training, not the large optimization campaign.

### Step 1. Resolve Front-End Bundle

Input:

- `repo_root`
- `array_id = Easycom`
- `hrtf_id = KU100`

Output:

- `front_end_bundle`
- `front_end_bundle.V[d, f, m]`
- `front_end_bundle.h[d, f, e]`
- `front_end_bundle.orientation_coefficients`

Required checks:

- all arrays are finite
- yaw `0` and yaw `90` entries exist
- each orientation entry matches the bundle coefficient shape

### Step 2. Select Orientation Coefficients

Input:

- `front_end_bundle`
- requested `yaw_deg`

Output:

- selected `OrientationCoefficientEntry`
- selected `c_ls[f, m, e]`
- selected `c_magls[f, m, e]`

Required checks:

- selected `c_magls` matches the saved reference for that yaw
- selected yaw `90` is not equal to the static yaw `0` default
- selected orientation metadata is retained for downstream export

### Step 3. Build Solver Input

The solver input pack must be defined as orientation-aware. The selected orientation entry is the coefficient source.

Required semantic inputs:

- selected `c_ls`
- selected `c_magls`
- selected `c_magls - c_ls`
- normalized frequency index
- normalized coefficient index
- optional front-end energy descriptor

Required packed channel names:

- `c_ls_left_re`
- `c_ls_left_im`
- `c_ls_right_re`
- `c_ls_right_im`
- `c_magls_left_re`
- `c_magls_left_im`
- `c_magls_right_re`
- `c_magls_right_im`
- `c_magls_minus_c_ls_left_re`
- `c_magls_minus_c_ls_left_im`
- `c_magls_minus_c_ls_right_re`
- `c_magls_minus_c_ls_right_im`
- `normalized_frequency_index`
- `normalized_coefficient_index`
- `front_end_energy_descriptor`, only when enabled

Required checks:

- packed channels reconstruct selected `c_magls`, not the static yaw `0` default unless yaw `0` was selected
- packed tensor shape is `[frequency, coefficient, channel]`
- channel list is exported in the smoke summary

### Step 4. Solver Forward

Input:

- `solver_input_packed`
- `ResidualSolverConfig`

Output:

- `delta_c[f, m, e]`
- `alpha`

Required checks:

- `delta_c` shape equals selected `c_magls` shape
- `delta_c` is finite
- `alpha` is finite and inside `[0, alpha_max]`
- backward pass is finite in focused test coverage

### Step 5. Compose Joint Coefficients

Definition:

```text
c_joint = c_magls + alpha * delta_c
```

Required checks:

- `c_joint` shape equals selected `c_magls` shape
- `c_joint` is finite
- no waveform-domain shortcut is introduced

### Step 6. Render Joint Response

Input:

- `front_end_bundle.V`
- `c_joint`

Output:

- `response_joint[d, f, e]`

Required checks:

- response shape matches target `h`
- response is finite
- renderer is the same BSM coefficient renderer used by baseline and learned branches

### Step 7. Compute Loss Breakdown

Required loss terms:

- `loss_mag`
- `loss_dmag`
- `loss_ild`
- `loss_itd`
- `loss_reg`
- `loss_total`

Required checks:

- all loss terms are finite
- total loss is the weighted sum of declared terms
- ILD path remains the ERB-band auditory cue authority for evaluation
- ITD path remains the GCC-PHAT proxy path already accepted in Phase 02

### Step 7A. Validate Short-Run Optimization Quality

`TASK-0008` must not stop at a finite forward/backward/export route. It must also establish that the short-run optimization has acceptable smoke-scale quality for the selected orientation.

Required quality checks:

- the selected-orientation short run must report a measurable optimization outcome, not merely write files
- at least one declared optimization-quality criterion must pass on the selected orientation run
- the criterion must be recorded explicitly in the session note and summary artifacts

Accepted quality criteria for `TASK-0008`:

- `loss_reduced = true`, or
- `final_loss_total <= initial_loss_total` together with stable cue and magnitude metrics and an explicit explanation of why equality or near-equality is acceptable for the current coefficient authority, or
- another predeclared short-run quality criterion accepted in the session note before execution

Minimum recorded metrics:

- `initial_loss_total`
- `final_loss_total`
- `selected_iteration`
- `loss_reduced`
- `ild_error`
- `itd_proxy_error`
- `normalized_magnitude_error`
- `nmse`

Failure policy:

- if the selected-orientation route is finite but quality is clearly poor or fully stagnant, `TASK-0008` is not accepted
- in that case the new implementation session must debug the route before the task can hand off to `TASK-0009`

### Step 8. Export Smoke Summary

The TASK-0008 smoke export must be smaller than the future TASK-0009 optimization logs, but it must prove the path is traceable.

Required fields:

- `schema_version`
- `interface_version`
- `producer_task_id = TASK-0008`
- `producer_session_id`
- `run_config_ref`
- `selected_orientation`
  - `yaw_deg`
  - `pitch_deg`
  - `roll_deg`
  - `c_ls_source`
  - `c_magls_source`
  - `reference_path`
  - `reference_sha256`
- `orientation_bank_yaws_deg`
- `solver_input_summary`
  - shape
  - channel names
  - coefficient source
- `solver_config`
- `loss_weights`
- `loss_trace_path`
- `summary_path`
- `metric_summary`
  - `ild_error`
  - `itd_proxy_error`
  - `normalized_magnitude_error`
  - `nmse`
- `task09_ready`
- `blocking_issues`

## Work Package 3. Minimal Validation Harness

The future implementation session should add the smallest route-specific validation needed for `TASK-0008`.

Preferred command shape:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --orientation-yaw-deg 90 --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

If adding `--orientation-yaw-deg` to `residual_solver smoke` is too invasive, the implementation may instead add a focused command in `bsm.phase02.correctness_validation` or a small TASK-0008 validator module. The command must still validate the same route and export the same orientation metadata.

Required artifact root:

```text
06_Assets/Generated_Artifacts/TASK-0008/<YYYYMMDDTHHMMSSZ>/
```

Required files:

- `summary.json`
- `loss_trace.jsonl`, if an optimization-step smoke is run
- `orientation_training_path.json`

`TASK-0008` does not need checkpoints, long-run logs, multi-run manifests, or ablation tables. Those are `TASK-0009` responsibilities.
It does need one explicit short-run quality judgment for the selected orientation route.

## Work Package 4. Documentation Updates During Execution

The implementation session must update:

- `00_Governance/Manifest/MANI-00_Project_State.md`
- `00_Governance/Manifest/MANI-02_Active_Focus.md`
- `00_Governance/Manifest/MANI-03_Continuation_Authority.md`
- `04_Tasks/Active/Index.md`
- `06_Assets/Generated_Artifacts/Index.md`, after TASK-0008 artifacts exist
- `05_Experiments/Registry/Result_Tracker.md`, only if an executable TASK-0008 validation run is recorded

Do not move `TASK-0007` or `TASK-0007A` to completed as part of `TASK-0008` unless the human listening review has also been recorded or the project owner explicitly accepts closing them.

## TASK-0009 Handoff

`TASK-0009` is the first task allowed to run large-scale planned neural optimization.

`TASK-0008` must hand off the following to `TASK-0009`:

- orientation-aware coefficient source is fixed
- solver input pack can be built from selected orientation entries
- yaw `0` and yaw `90` route checks pass
- smoke export includes selected orientation metadata
- loss trace fields are stable
- short-run optimization quality has been judged acceptable and recorded
- artifact directory structure is fixed

`TASK-0009` must own:

- orientation grid expansion beyond yaw `0` and yaw `90`
- long-run iteration counts
- planned run matrix
- checkpoint frequency and checkpoint format
- random seed policy
- optimizer schedule
- loss-weight schedule
- ablation table
- run registry updates for every large run
- detailed log review and comparison plots
- formal comparison against BSM-MagLS, saved eMagLS, and later BSM-iMagLS coefficient entries

## Predeclared Test Standard

Type:

- Contract conformance plus optimization-readiness smoke

Preconditions:

- `bsm_harness_py311` is available
- `TASK-0007` machine gates have passed
- saved aligned-ypr yaw `0` and yaw `90` reference files exist
- full discovered tests currently pass

Required checks:

- yaw `0` and yaw `90` orientation entries are present
- `select_orientation_coefficients(..., yaw_deg=90)` returns yaw `90`, not yaw `0`
- selected yaw `90` coefficient parity against the saved yaw `90` reference is zero error
- solver input channels reconstruct selected `c_magls`
- forward and backward pass are finite on the selected orientation
- joint rendering and loss breakdown are finite
- export summary contains selected orientation metadata
- short-run optimization quality is evaluated explicitly and recorded
- if the selected orientation short run fails to reduce loss or otherwise fails the predeclared quality criterion, the session must debug the route before claiming TASK-0008 acceptance

Completion gate:

- one TASK-0008 execution session records the commands, pass/fail results, and artifact paths
- the full discovered test suite passes after implementation
- generated TASK-0008 artifacts are indexed if artifacts are produced
- the session records a clear short-run optimization quality conclusion for the selected orientation route
- `TASK-0009` handoff is precise enough to start planned large-scale optimization without redefining the training route

## Current Manual Checks Already Available

The following command has already confirmed selected yaw `90` parity in the current workspace:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.correctness_validation diagnose-emagls --yaw-deg 90 --indent 2
```

Observed result:

- `max_abs = 0.0`
- `mean_abs = 0.0`
- `nmse = 0.0`

The full discovered tests have also passed in the current workspace:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

Observed result:

- `28` tests passed

These checks were useful starting evidence but did not close `TASK-0008` by themselves.

## 2026-04-21 Execution Result

The required execution session now exists at:

- `03_Sessions/Phase_02_Development/SESSION-P2-0009_Orientation_Training_Path_Smoke.md`

Accepted command:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --orientation-yaw-deg 90 --iterations 24 --learning-rate 0.001 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

Recorded artifact directory:

- `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/`

Observed result:

- `ok = true`
- `initial_loss_total = 3.4457359313964844`
- `final_loss_total = 3.0254967212677`
- `selected_iteration = 24`
- `loss_reduced = true`
- `normalized_magnitude_error = 0.34547776114508993`
- `nmse = 1.636918544769287`
- `ild_error = 9.372719879973232`
- `itd_proxy_error = 0.018850489522542212`
- `task09_ready = true`

Short-run quality conclusion:

- The selected yaw `90` route now shows actual smoke-scale loss reduction after slightly extending the optimization horizon and reducing the learning rate.
- `TASK-0008` has therefore satisfied its requirement to judge short-run optimization quality explicitly on the selected orientation path.

## Execution Status

- Machine-side orientation-aware validation has been recorded.
- The next continuation step should hand off to `TASK-0009` planning rather than redesigning the `TASK-0008` route.
- Human listening remains owner-run and is not a TASK-0008 machine blocker.
