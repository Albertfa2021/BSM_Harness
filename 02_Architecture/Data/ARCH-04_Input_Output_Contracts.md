---
Document_ID: ARCH-04
Title: Input Output Contracts
Status: Draft
Phase: Phase_02_Development
Track: Architecture
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Distillations/DIST-0002_Phase01_Architecture_Baseline.md
  - 01_Charter/Goals/CHAR-06_Phase_01_Execution_Plan.md
  - 02_Architecture/Data/ARCH-03_Data_Schema.md
  - 06_Assets/Generated_Artifacts/Index.md
  - 04_Tasks/Active/TASK-0008_Orientation_Coefficient_Bank_And_Training_Path.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# Input Output Contracts

## Contract Principle

- Contracts are defined at the semantic level so that implementation can change without breaking experiment traceability.
- Cross-session interfaces must be serializable, versioned, and named with the canonical schema terms from `ARCH-03`.

## Cross-Session Interface Rule

- If one session produces output for a later session to consume, that output must be exposed through a declared contract in this document.
- Ad-hoc notebook variables, unnamed dictionaries, or manually remembered shapes are not acceptable handoff interfaces.
- Every reusable contract output must be accompanied by:
  - `schema_version`
  - `interface_version`
  - `producer_task_id`
  - `producer_session_id`
  - `run_config_ref`

## Variable Discipline Rule

- Interface field names must match the canonical object names in `ARCH-03`.
- If a module uses a packed or transformed internal representation, it must:
  - keep the public contract name for the semantic object
  - describe the transformation explicitly in the module or session note
- Example:
  - public semantic object: `c_magls`
  - model-side packed tensor: `solver_input_packed`
  - not acceptable: renaming `c_magls` to an undocumented generic `x`

## Contract 1. Asset Resolver

- Input:
  - environment name
  - asset identifiers
  - reference paths
- Output:
  - validated asset bundle
- Required checks:
  - all referenced files exist
  - environment is `bsm_harness_py311`
  - asset identifiers match Phase 01 defaults unless explicitly overridden in an experiment

## Contract 2. Front-End Builder

- Input:
  - asset bundle
  - static direction grid specification
  - baseline configuration
- Output:
  - front-end bundle with `grid`, `V`, `h`, `c_ls`, `c_magls`
- Required checks:
  - direction count matches all grid-dependent tensors
  - `h`, `c_ls`, and `c_magls` reference the same acoustic target configuration
  - shapes are internally consistent across frequency and ear axes
  - exported field names match the schema names exactly

## Contract 2A. Orientation Coefficient Bank

- Input:
  - orientation grid or requested yaw/pitch/roll
  - front-end asset bundle
  - coefficient authority selection
  - DNN-solver configuration for iMagLS entries
- Output:
  - orientation-keyed coefficient bank
  - each coefficient entry has canonical shape `[frequency, microphone, ear]`
  - each entry records:
    - `yaw_deg`
    - `pitch_deg`
    - `roll_deg`
    - `coefficient_source`
    - `solver_source`
    - `reference_path`, when loaded from a saved reference
    - `validation_metrics`
- Selection contract:
  - static default callers may continue to consume `front_end_bundle.c_magls` as yaw `0`
  - any rotation-specific caller must select from the orientation bank
  - exact yaw selection is the accepted TASK-0008 policy for yaw `0` and yaw `90`
  - unavailable yaw values must fail loudly rather than falling back to yaw `0`
- Required checks:
  - yaw `0` entry preserves the saved aligned-ypr coefficient parity contract
  - yaw `90` entry is not silently substituted with yaw `0`
  - `c_ls`, `c_magls`, and any `c_imagls` entry for a given orientation use compatible source semantics
  - DNN-generated iMagLS coefficients are precomputed and exported before playback/inference
  - playback/inference selects coefficients from head-tracker yaw/pitch/roll state instead of running online optimization
- Current implementation status:
  - saved aligned-ypr eMagLS yaw `0` and yaw `90` entries are available through `front_end_bundle.orientation_coefficients`
  - exact yaw selection is available through `select_orientation_coefficients(...)`
  - BSM-iMagLS DNN-generated entries are not implemented yet and must be added as a later coefficient type in the bank
  - `TASK-0008` is responsible for wiring selected orientation entries through the neural training-path smoke and judging short-run optimization quality before `TASK-0009`

## Contract 3. Baseline Renderer

- Input:
  - front-end bundle
  - selected baseline coefficients
- Output:
  - rendered baseline binaural responses
  - baseline-side metrics
- Required checks:
  - coefficient set is traceable to `LS` or `MagLS`
  - renderer uses the same front-end semantics as the learned branch

## Contract 4. Residual Solver

- Input:
  - `c_magls`
  - allowed condition features
- Output:
  - `delta_c`
  - optional scalar or scheduled `alpha`
- Required checks:
  - solver output matches `c_magls` coefficient semantics
  - no direct binaural waveform output is emitted by this module
  - packed model inputs are documented separately from the semantic input objects
  - for head-tracked BSM-iMagLS, each orientation is solved as its own coefficient-entry case unless a later experiment validates a global orientation-conditioned solver
  - TASK-0008 training-path smoke must prove that packed `c_magls_*` channels reconstruct the selected orientation entry, not an implicit static yaw `0` coefficient object

## Contract 5. Joint Coefficient Composer

- Input:
  - `c_magls`
  - `delta_c`
  - `alpha`
- Output:
  - `c_joint`
- Required checks:
  - update rule is `c_joint = c_magls + alpha * delta_c`
  - resulting coefficient shape is identical to baseline coefficient shape

## Contract 6. Joint Renderer

- Input:
  - front-end bundle
  - `c_joint`
- Output:
  - joint binaural response on the same direction grid
- Required checks:
  - evaluation grid exactly matches baseline grid
  - output ear and frequency semantics match `h`

## Contract 7. Loss Bank

- Input:
  - rendered joint response
  - target response `h`
  - auditory ILD helper outputs
  - ITD proxy helper outputs
  - regularization configuration
- Output:
  - loss breakdown
- Required checks:
  - total loss is the weighted sum of declared loss terms
  - loss terms are finite
  - ILD path uses ERB-band auditory analysis semantics
  - ITD path uses the accepted Phase 01 differentiable proxy
  - TASK-0008 must record whether the selected-orientation short run shows acceptable smoke-scale optimization quality, not merely finite execution

## Contract 8. Evaluation And Logging

- Input:
  - baseline responses
  - joint responses
  - loss traces
  - run configuration
- Output:
  - metric summary
  - trace artifact references
  - experiment record updates
- Required checks:
  - comparison baseline is explicitly named
  - objective metrics include ILD error, ITD proxy error, normalized magnitude error, and NMSE
  - artifacts are linked back to the experiment registry
  - any cross-session export includes version and producer metadata
  - orientation-aware runs must export selected yaw/pitch/roll, coefficient source metadata, available orientation-bank yaws, solver input channel names, and loss weights
  - TASK-0008 exports must also include a short-run quality conclusion or the raw fields needed to make that conclusion (`initial_loss_total`, `final_loss_total`, `selected_iteration`, `loss_reduced`)
  - large-run checkpointing, run matrices, and detailed optimization logs are owned by `TASK-0009`, not by the TASK-0008 smoke contract
