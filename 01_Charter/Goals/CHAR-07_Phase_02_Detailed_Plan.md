---
Document_ID: CHAR-07
Title: Phase 02 Detailed Plan
Status: Draft
Phase: Phase_02_Development
Track: Charter
Maturity: Consolidating
Related_Docs:
  - 01_Charter/Goals/CHAR-06_Phase_01_Execution_Plan.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/Index.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md
  - 05_Experiments/EXP-0001_Auditory_ILD_Python/README.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 07_References/Open_Source_Baselines/BAS-0002_ILD_Auditory_Method.md
  - 07_References/Papers/Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf
Last_Updated: 2026-04-20
Review_Required: Yes
---

# Phase 02 Detailed Plan

## Purpose

- Fix the concrete Phase 02 execution order for turning the accepted Phase 01 architecture into a runnable project-side implementation.
- Record what is already implemented from the reference material and what is still missing.
- Freeze the accepted neural-solver shape so later implementation does not drift into an ordinary flat MLP.

## Current Truth On 2026-04-20

- The repository now has a smoke-scale project-side runnable loop.
- `Array2Binaural` remains a read-only reference tree, with project-side wrappers in `bsm.phase02`.
- The following accepted Phase 01 components are now implemented and smoke-tested in the formal project work area:
  - asset resolver and run validator
  - unified BSM front-end bundle builder
  - project-side `BSM-LS` and `BSM-MagLS` reproduction wrapper
  - differentiable ITD proxy path
  - residual neural solver
  - joint optimization loop
  - experiment logging and metric registry integration
- This is a first verified implementation closure, not a final numerical-quality or generalization claim.

## Reference Realization Summary

| Area | Main reference | Current project status | Phase 02 decision |
| --- | --- | --- | --- |
| Auditory ILD | `ILD computer method`, `BAS-0002` | Implemented in Python and promoted into `bsm.phase02.cue_bank` | Keep the reference tree read-only and preserve ERB-band evaluation semantics |
| Baseline front-end | `Array2Binaural`, `BAS-0001` | Wrapped through `bsm.phase02.front_end_bundle` | Keep upstream tree read-only and use project-side wrappers |
| `BSM-LS` / `BSM-MagLS` | `Array2Binaural` | Exposed through project contracts and shared renderer | Treat as the canonical comparison baseline |
| ITD proxy | `Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction` | Implemented through GCC-PHAT sequence-MSE path | Keep as the first accepted differentiable ITD implementation |
| Joint solver | Internal plan only | Implemented through `bsm.phase02.residual_solver` | Treat as smoke-scale closure pending review and ablation |
| Evaluation closure | Architecture docs only | Summary and trace export implemented for `TASK-0006` | Use machine-readable exports as the source for later notebooks or Phase 03 evaluation |

## Required Anchors For The Next Implementation Pass

| Implementation area | Mandatory anchor content | What must be reproduced or wrapped |
| --- | --- | --- |
| Asset resolution | `Array2Binaural/README.md`, `DEP-0001` | environment name, required asset filenames, Easycom SH file generation prerequisite, external data download expectations |
| Static evaluation grid | `Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py` | equatorial direction sweep used for objective comparison |
| Baseline optimization grid | `Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py` | `spaudiopy.grids.load_n_design(35)` style design grid for coefficient solving |
| Array steering/front-end tensors | `Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py` | decoded steering responses `d`, rotated SH handling, mic-delay alignment, KU100 HRIR decoding |
| Baseline rendering semantics | `Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py` | frequency-domain coefficient application to steering responses and ear-wise rendering |
| Baseline filter generation | `Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py` | LS below cutoff, MagLS above cutoff, diffuse-field equalization |
| Auxiliary beamforming filters | `Array2Binaural/ild_itd_analysis/compute_filters.py` | keep as read-only study anchor only; do not let it redefine the accepted joint path |
| ILD cue path | `BAS-0002`, `EXP-0001_Auditory_ILD_Python` | ERB spacing, filterbank design, per-band energy ILD computation |
| ITD cue path | `Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf` | GCC-PHAT cross-correlation computation and sequence-domain MSE loss |

## Plan-Driven Rules For Areas Without Direct References

- If an implementation area has no direct external script or paper anchor, it must be derived from `01_Charter/Goals/20260324_BSM_Neural_Optimization_Plan.md`, not improvised locally.
- The governing sections are:
  - Section 四 `总体技术路线`: preserve the chain `initial coefficients -> residual network -> corrected coefficients -> BSM rendering -> ILD/ITD/MSE losses`
  - Section 五 `输入输出设计`: use coefficient-domain inputs plus condition descriptors; output only the coefficient residual `Δw`
  - Section 六 `损失函数设计`: total loss must include ILD, ITD, MSE, and regularization
  - Section 七 `实验设计`: keep baseline comparisons and internal ablations explicit
- This rule governs:
  - solver input packing
  - residual network topology
  - residual regularization
  - evaluation export schema
  - ablation and acceptance configuration

## How Phase 02 Proceeds When No Direct Reference Exists

- Not every Phase 02 step has a one-to-one external reference.
- For steps without a direct external code or paper anchor, the implementation rule is:
  - inherit semantic contracts from `ARCH-01` to `ARCH-06`
  - mirror upstream naming and tensor meaning where the baseline already implies them
  - add the thinnest project-side wrapper that preserves traceability
  - validate each new module first with smoke tests and shape checks before integrating it into the optimization loop
- This rule applies especially to:
  - asset resolver
  - solver input packer
  - residual solver backbone
  - evaluation trace writer
- These modules are project integration work, not literature reproduction work, so correctness is defined by:
  - contract consistency
  - numerical stability
  - compatibility with the shared renderer and cue bank

## Fixed Phase 02 Scope

- Stay with `Easycom + KU100`.
- Stay with static direction sets and single-instance optimization.
- Keep `BSM-MagLS` as the canonical initializer.
- Keep objective-first validation; subjective evaluation remains out of scope.
- Do not replace the renderer with a waveform model.

## Execution Cadence

- Phase 02 implementation advances by session-scoped subtasks, not by multi-module bursts.
- Each implementation session must:
  - select exactly one active task
  - declare its test standard before coding
  - run the declared tests before closing the session
- The active task chain is maintained in `04_Tasks/Active/`.
- The governing rule is fixed by `PROT-03_Session_Scoped_Subtask_Execution.md`.

## Accepted Phase 02 Work Packages

### WP1. Resolve And Freeze External Assets

- Add a project-side resolver that checks:
  - active environment
  - required array-transfer assets
  - KU100 HRIR assets
  - imported baseline paths
- Exit gate:
  - one call returns a validated asset bundle
  - missing files fail early with traceable messages

### WP2. Wrap The BSM Front-End

- Extract a project-side front-end builder around the reference semantics.
- The builder must expose:
  - static direction grid
  - `V`
  - `h`
  - `c_ls`
  - `c_magls`
- Exit gate:
  - the bundle can be rebuilt deterministically for the same config
  - `c_ls` and `c_magls` render through the same project-side renderer entry
- Mandatory anchors:
  - `Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py`
  - `Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py`
- Required reproduction details:
  - Easycom SH-domain array response loading
  - KU100 SH-HRIR loading and ear decoding
  - mic-delay and HRIR-delay alignment semantics
  - coefficient tensors stored in project-side canonical shapes

### WP3. Promote Cue Analysis Into Formal Modules

- Reuse the existing auditory ILD Python path as the canonical ERB-band ILD implementation.
- Reproduce the ITD-loss paper path with the same two-step logic:
  - compute interaural cross-correlation with GCC-PHAT
  - use MSE between reference and estimated cross-correlation sequences as the differentiable ITD loss
- Keep the paper-side delay window parameter `tau` explicit in config and logging.
- Use the paper as the first implementation anchor, not a looser in-house proxy.
- Exit gate:
  - ILD and ITD helpers both accept rendered binaural responses and target responses under one shared tensor contract
  - both paths return finite values and can be used inside autograd-ready loss code

## Why Phase 02 Uses The ITD-Loss Paper Path

- The cited paper defines ITD conceptually by the lag of the cross-correlation peak, but avoids direct `argmax` in training because it is non-differentiable.
- Its actual differentiable loss is the MSE between reference and estimated GCC-PHAT cross-correlation sequences.
- That makes it the right Phase 02 starting point for this project because:
  - it is already aligned with our accepted objective family in `CHAR-06`
  - it stays in the binaural-cue domain instead of forcing a phase-only surrogate
  - it is differentiable end to end through FFT and IFFT
  - it is more implementation-stable than trying to optimize a discrete ITD peak directly
- Phase 02 therefore does not choose GCC-PHAT because it is arbitrary.
- It chooses GCC-PHAT cross-correlation MSE because that is the concrete training formulation used by the reference ITD-loss paper.

### WP4. Implement The Joint Solver

- Build the accepted residual model over `c_magls`.
- Keep the output in coefficient space only.
- Use `c_joint = c_magls + alpha * delta_c`.
- Since there is no direct external solver reference, implement this package strictly from:
  - Section 四 `总体技术路线`
  - Section 五 `输入输出设计`
  - Section 六 `损失函数设计`
  - Section 七 `实验设计`
- Required outcome:
  - preserve the project’s position as coefficient-domain neural optimization, not end-to-end waveform prediction
  - keep `alpha` explicit for ablation
- Exit gate:
  - solver output shape exactly matches `c_magls`
  - one optimization run reduces at least the total loss against its own initialization on a smoke configuration

### WP5. Close Evaluation And Traceability

- Log baseline metrics, joint metrics, per-loss traces, and residual norms.
- Register outputs into `05_Experiments/Registry/`.
- Exit gate:
  - each run records its baseline, loss weights, `alpha`, and artifact locations
  - `BSM-MagLS` versus joint comparison is exportable without manual notebook patching

## Phase 02 Internal Slices

### Slice 1. Reference-Wrapped Static Core

- Finish asset resolution, static grids, front-end bundle, `BSM-LS`, `BSM-MagLS`, and shared renderer.
- This slice is the minimum required before any neural optimization claims are valid.

### Slice 2. Paper-Aligned ITD Core

- Add the GCC-PHAT ITD loss exactly as the differentiable implementation anchor from the ITD-loss paper.
- This slice closes the first accepted ILD + ITD + signal-fidelity objective loop.

### Slice 3. Plan-Driven ITD Variants And Ablations

- After the paper-aligned ITD core is stable, expand to the variable ITD design already fixed in `20260324_BSM_Neural_Optimization_Plan.md`:
  - `ITD-A`: direction-response cross-correlation ITD
  - `ITD-B`: low-frequency group-delay or phase-slope ITD
- These are not allowed to replace Slice 2 before the paper-aligned path is closed.

## Accepted Neural Solver Shape

### Name

- `FCR-Mixer`: Frequency-Conditioned Complex Residual Mixer

### Why This Shape Is Accepted

- The task is coefficient refinement, not waveform generation.
- The model must couple three structures at once:
  - smooth evolution across frequency
  - interaction across coefficient index `m`
  - binaural coupling between left and right coefficient branches
- A plain flattened MLP would ignore this structure and make regularization harder.

### Canonical Input Tensor

- Start from project-side semantic coefficients:
  - `c_ls[f, m, e]`
  - `c_magls[f, m, e]`
- Convert complex coefficients into real channels:
  - `re/im(c_ls)` for left and right ears
  - `re/im(c_magls)` for left and right ears
  - `re/im(c_magls - c_ls)` for left and right ears
- Append scalar descriptors:
  - normalized log-frequency index
  - normalized coefficient index
  - optional front-end energy descriptor per frequency
- Accepted packed model input:
  - `x0[f, m, c_in]`
  - default `c_in = 14` without the optional descriptor
  - `c_in = 15` when the optional descriptor is enabled

### Canonical Hidden Shape

- Lift `x0` to `hidden_dim = 96`.
- Stack `6` residual mixer blocks.
- Each block contains:
  - coefficient-axis mixing over `m`
  - dilated frequency-axis `Conv1d` over `f` with dilation cycle `{1, 2, 4}`
  - ear-coupling gate so left/right residuals are not learned independently
- Keep pre-normalization and residual connections in every block.

### Output Head

- Use two residual heads:
  - local head `delta_local[f, m, 4]`
  - low-rank global head with rank `r = 8`
- Compose them with a learned sigmoid gate:
  - `delta = gate * delta_local + (1 - gate) * delta_global`
- Interpret the final `4` output channels as:
  - `re(delta_c_left)`
  - `im(delta_c_left)`
  - `re(delta_c_right)`
  - `im(delta_c_right)`

### Accepted `alpha`

- `alpha` is a learnable scalar gate shared by the whole run.
- Initialize `alpha = 0.15`.
- Clamp or reparameterize it into `[0.0, 0.35]`.
- `alpha` stays explicit in logs and ablations.

## Required Phase 02 Acceptance Checks

1. Front-end smoke test:
   - assets resolve
   - bundle shapes are internally consistent
   - baseline rendering runs without `nan/inf`
2. Cue smoke test:
   - ILD path matches the existing auditory replication expectations
   - ITD proxy path returns stable finite sequences on simple binaural examples
3. Solver smoke test:
   - one backward pass is finite
   - one short optimization run reduces total loss relative to initialization
4. Evaluation gate:
   - exports `ild_error`, `itd_proxy_error`, `normalized_magnitude_error`, and `nmse`
   - records per-loss traces and residual norms

## Deferred Items

- dynamic yaw trajectories
- `ITD-A` versus `ITD-B` multi-definition comparison
- multi-array or multi-HRTF generalization
- subjective listening workflow
- real-time deployment
