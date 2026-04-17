---
Document_ID: ARCH-07
Title: Phase 02 Implementation Blueprint
Status: Draft
Phase: Phase_02_Development
Track: Architecture
Maturity: Consolidating
Related_Docs:
  - 01_Charter/Goals/CHAR-07_Phase_02_Detailed_Plan.md
  - 02_Architecture/Logic/ARCH-02_Method_Pipeline.md
  - 02_Architecture/Data/ARCH-03_Data_Schema.md
  - 02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/Index.md
  - 05_Experiments/EXP-0001_Auditory_ILD_Python/README.md
  - 07_References/Papers/Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Phase 02 Implementation Blueprint

## Goal

- Turn the accepted Phase 01 architecture into an ordered implementation blueprint for the current development phase.
- Fix, stage by stage, which reference content is already realized and which parts still need project-side implementation.

## Stage Audit Against References

| Stage | Accepted reference anchor | Current realization in this repo | Status |
| --- | --- | --- | --- |
| Stage 0. Resolve assets and environment | `DEP-0001`, `BAS-0001` | Environment and dependency assumptions are documented, but no project-side validator exists yet | Partial |
| Stage 1. Prepare static direction grid | `Array2Binaural` direction usage, `ARCH-03` semantic grid | Grid semantics are documented only | Not implemented |
| Stage 2. Build front-end bundle | `Array2Binaural` front-end path, `ARCH-01`, `ARCH-04` | No project module yet exposes `grid`, `V`, `h`, `c_ls`, `c_magls` together | Not implemented |
| Stage 3. Render baseline responses | `Array2Binaural` baseline rendering path | No project-side baseline renderer wrapper yet | Not implemented |
| Stage 4. Assemble solver inputs | Internal architecture plan plus project-side tensor contracts from `ARCH-03` and `ARCH-04` | Input semantics are documented only | Not implemented |
| Stage 5. Predict residual coefficients | `CHAR-06`, `CHAR-07` | No solver code yet | Not implemented |
| Stage 6. Form joint coefficients | `CHAR-06` update rule | Formula is fixed in docs, not yet wired in code | Not implemented |
| Stage 7. Render joint responses | Shared renderer concept in `ARCH-06` | No joint renderer entry exists yet | Not implemented |
| Stage 8. Compute baseline metrics | `BAS-0002`, existing ILD experiment | Standalone auditory ILD path exists, but not connected to the BSM baseline path | Partial |
| Stage 9. Compute joint losses and metrics | `BAS-0002`, ITD-loss paper Eq. (15) and Eq. (16) | ILD path exists; ITD proxy and integrated loss bank do not | Partial |
| Stage 10. Compare against `BSM-MagLS` | `ARCH-02`, `CHAR-06` | Comparison rule is documented only | Not implemented |
| Stage 11. Store traces and summaries | `EXP-Registry`, `Result_Tracker` | Registry exists, but no run writer exists yet | Not implemented |

## File-Level Anchor Map

| Project concern | Anchor file | Anchored content |
| --- | --- | --- |
| Asset downloads and generated prerequisites | `07_References/Open_Source_Baselines/Array2Binaural/README.md` | third-party data expectations and generation of `Easycom_array_32000Hz_o25_22samps_delay.npy` |
| Optimization grid and baseline coefficient construction | `07_References/Open_Source_Baselines/Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py` | n-design optimization grid, HRTF decoding, LS/MagLS split by frequency, diffuse-field equalization |
| Evaluation grid and rendered binaural comparison | `07_References/Open_Source_Baselines/Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py` | equatorial direction sweep, rendered left/right response formation, baseline-side ILD/ITD evaluation semantics |
| Auxiliary beamforming and residual filters | `07_References/Open_Source_Baselines/Array2Binaural/ild_itd_analysis/compute_filters.py` | read-only study anchor for BFBR, LCMV, and residual filter structure |
| Auditory ILD replication | `05_Experiments/EXP-0001_Auditory_ILD_Python/code/auditory_ild.py` | project-side ERB-band ILD implementation |
| ITD differentiable loss | `07_References/Papers/Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf` | Eq. (15) GCC-PHAT cross-correlation and Eq. (16) sequence-MSE ITD loss |
| No-direct-reference design source | `01_Charter/Goals/20260324_BSM_Neural_Optimization_Plan.md` | coefficient-domain optimization route, input/output policy, loss composition, ablation policy |

## Consequence Of The Audit

- The project has implemented one important reference branch correctly: auditory ILD analysis.
- The project has not yet implemented the actual Phase 01 runnable loop.
- Therefore Phase 02 must prioritize project-side wrapping and integration over adding more theoretical variants.

## Strategy For Stages Without A Direct External Reference

- Some Phase 02 stages are integration stages rather than literature-reproduction stages.
- For these stages, the implementation strategy is fixed as follows:
  - derive inputs and outputs from `ARCH-03` and `ARCH-04`
  - preserve the semantic names already frozen in `ARCH-01`, `ARCH-02`, and `ARCH-06`
  - prefer minimal wrappers around baseline semantics instead of inventing new abstractions
  - require one isolated smoke test before wiring the stage into downstream modules
  - use `20260324_BSM_Neural_Optimization_Plan.md` as the design authority for network input/output, loss composition, and ablation structure
- The no-direct-reference stages are:
  - Stage 0 asset resolver
  - Stage 4 solver input assembly
  - Stage 5 residual solver
  - Stage 10 comparison writer
  - Stage 11 trace and registry writer
- Their acceptance source is project contract compliance, not external code parity.

## Accepted Implementation Order

- The following steps are not only architectural order.
- They are also the required session order unless a task is explicitly blocked.

### Step A. Asset Resolver

- Build one project-side function that returns:
  - `array_id`
  - `hrtf_id`
  - resolved asset paths
  - environment name
- Failure policy:
  - fail before any rendering or optimization starts
- No-direct-reference implementation rule:
  - read asset names and path expectations from `DEP-0001`, `BAS-0001`, and current imported-tree filenames
  - keep the resolver declarative and side-effect free
- Mandatory checks:
  - `Device_ATFs.h5` exists where the baseline README expects it
  - `Easycom_array_32000Hz_o25_22samps_delay.npy` exists or has a registered generation path
  - `ku100_magls_sh_hrir/irsOrd5.wav` exists
  - `bsm_harness_py311` is the active conda environment

### Step B. Direction Grids

- Maintain two distinct grids:
  - optimization grid for coefficient solving
  - static evaluation grid for reporting metrics
- Optimization grid anchor:
  - `compute_emagls2_for_rotations.py` uses `spaudiopy.grids.load_n_design(35)`
- Evaluation grid anchor:
  - `evaluate_ilds_itds.py` uses equatorial `source_dir = np.arange(-180, 180, 5)`
- Phase 02 project decision:
  - keep the n-design grid for baseline coefficient construction
  - keep the equatorial 5-degree grid as the default static reporting grid

### Step C. Front-End Bundle Builder

- Build one bundle object with:
  - `grid[d]`
  - `V[d, f, m]`
  - `h[d, f, e]`
  - `c_ls[f, m, e]`
  - `c_magls[f, m, e]`
- This bundle is the mandatory handoff object for both baseline and learned branches.
- Mandatory anchor content:
  - HRTF SH decoding and delay alignment from `compute_emagls2_for_rotations.py`
  - steering response construction from `compute_emagls2_for_rotations.py`
- Required project-side canonicalization:
  - store complex coefficients and responses in stable axis order
  - expose both optimization and evaluation grids without changing renderer semantics

### Step D. Baseline Coefficient Builder

- Project-side builder must expose:
  - `c_ls`
  - `c_magls`
- Mandatory anchor content from `compute_emagls2_for_rotations.py`:
  - LS solve below frequency cutoff
  - recursive MagLS phase continuation above cutoff
  - diffuse-field equalization after solving
- Phase 02 canonicalization:
  - static core uses the yaw=`0`, pitch=`0`, roll=`0` slice as the initial baseline target
  - later orientation sweeps remain an extension, not the first acceptance target

### Step E. Shared Renderer

- Expose one renderer entry:
  - input: `front_end_bundle`, `coefficients[f, m, e]`
  - output: `response[d, f, e]`
- Use the same entry for:
  - `c_ls`
  - `c_magls`
  - `c_joint`
- Mandatory anchor content:
  - ear-wise rendering pattern from `evaluate_ilds_itds.py`
  - renderer semantics reduce to applying coefficient weights to steering responses per ear

### Step F. Cue Bank

- Promote the existing auditory ILD path into a reusable cue module.
- Add ITD-loss-paper support with the same computation path used in the paper:
  - compute GCC-PHAT cross-correlation sequence `c`
  - restrict the loss to the configured lag window `[-tau, tau]`
  - compute MSE between reference and estimated sequences
- Keep both under one response-domain interface:
  - input: rendered or target binaural responses
  - output: cue tensors and scalar metrics
- Mandatory anchor split:
  - ILD path follows `auditory_ild.py`
  - ITD path follows the ITD-loss paper
- Phase 02 extension reserve from `20260324_BSM_Neural_Optimization_Plan.md`:
  - allow later addition of `ITD-A` and `ITD-B`
  - do not conflate those later variants with the first accepted differentiable ITD path

### Step F1. ITD-Loss Paper Alignment

- Paper-side conceptual definition:
  - ITD is the lag of the highest cross-correlation peak within `[-tau, tau]`
- Paper-side training definition:
  - do not optimize the discrete peak location directly
  - optimize MSE between GCC-PHAT cross-correlation sequences instead
- Accepted Phase 02 implementation:
  - reproduce the paper training definition first
  - keep direct peak-picking ITD only as an evaluation metric if needed
- Required configuration:
  - sample rate
  - `tau` in seconds and samples
  - optional low-frequency prefilter toggle if later experiments require it

### Step G. Solver Input Assembly

- No direct external script exists for this packer.
- Implementation authority:
  - Section 四 `总体技术路线`
  - Section 五 `输入输出设计`
- Required project-side input pack:
  - `c_ls`
  - `c_magls`
  - `c_magls - c_ls`
  - normalized frequency index
  - normalized coefficient index
  - optional front-end energy descriptor
- Explicit non-goal:
  - do not pack rendered waveforms as the primary solver input

### Step H. Residual Solver

- Accepted solver input pack:
  - `c_ls`
  - `c_magls`
  - normalized frequency index
  - normalized coefficient index
  - optional per-frequency front-end energy descriptor
- Accepted solver output:
  - `delta_c[f, m, e]`
  - scalar `alpha`
- No-direct-reference implementation rule:
  - use architecture-fixed tensor semantics as the source of truth
  - follow `20260324_BSM_Neural_Optimization_Plan.md` Section 五 for input/output policy
  - follow Section 六 for regularization requirements
  - evaluate success by loss reduction, gradient stability, and renderer compatibility

### Step I. Loss Bank And Optimization Loop

- Total loss:
  - `loss_total = w_mag * loss_mag + w_dmag * loss_dmag + w_ild * loss_ild + w_itd * loss_itd + w_reg * loss_reg`
- Required logs per iteration:
  - `loss_total`
  - `loss_mag`
  - `loss_dmag`
  - `loss_ild`
  - `loss_itd`
  - `loss_reg`
  - residual norm
  - `alpha`
- Design authority:
  - Section 六 `损失函数设计`
  - Section 七 `实验设计`
- Phase 02 project interpretation:
  - `loss_mag` and `loss_dmag` are the signal-fidelity terms already fixed by the architecture
  - `loss_ild` and `loss_itd` are the spatial-information terms
  - `loss_reg` must include at least residual magnitude and frequency smoothness penalties

### Step J. Evaluation Export

- Required summary fields:
  - `baseline_name`
  - `ild_error`
  - `itd_proxy_error`
  - `normalized_magnitude_error`
  - `nmse`
  - `loss_trace_path`
  - `artifact_refs`
- No-direct-reference implementation rule:
  - write structured machine-readable outputs first
  - let any later notebook or visualization consume these exports rather than becoming part of the core path
- Design authority:
  - Section 七 `实验设计`
- Phase 02 export minimum:
  - external baseline comparison
  - internal ablation tags for `alpha`, ITD mode, and regularization choice

## Accepted Neural Shape

### Canonical Representation

- Keep coefficient semantics complex until model packing time.
- Pack complex coefficients into real channels:
  - `c_ls -> 4 channels`
  - `c_magls -> 4 channels`
  - `c_magls - c_ls -> 4 channels`
- Append positional descriptors:
  - one normalized frequency channel
  - one normalized coefficient-index channel
- Default packed tensor:
  - `x0[f, m, 14]`

### `FCR-Mixer` Backbone

- Lift: `Linear(14 -> 96)`
- Backbone depth: `6` blocks
- Per block:
  - `LayerNorm`
  - coefficient mixer MLP on the `m` axis
  - dilated `Conv1d` on the `f` axis with kernel size `3`
  - binaural gate for left/right coupling
  - residual skip

### Global-Local Residual Head

- Local head:
  - `Linear(96 -> 64 -> 4)`
- Global head:
  - predict `u[f, r, 4]` and `v[m, r]`
  - use rank `r = 8`
  - `delta_global[f, m, 4] = sum_r u[f, r, 4] * v[m, r]`
- Final blend:
  - `delta = gate * delta_local + (1 - gate) * delta_global`

### Output Contract

- Convert output channels back to:
  - `delta_c[f, m, left]`
  - `delta_c[f, m, right]`
- Compose:
  - `c_joint = c_magls + alpha * delta_c`

## Architectural Reasons For This Shape

- Frequency dilated mixing enforces smooth spectral corrections instead of jagged bin-wise noise.
- Coefficient-axis mixing lets the model reshape energy across the BSM coefficient basis rather than editing each coefficient independently.
- The low-rank global head captures broad correction structure that is likely to repeat across `m`.
- The local head preserves the ability to make narrow-band or narrow-basis corrections.
- Explicit binaural coupling is appropriate because the optimization target is binaural cue preservation, not two unrelated mono branches.

## Implementation Guardrails

- Do not implement waveform-domain direct prediction.
- Do not add dynamic yaw inputs in this phase.
- Do not let the cue bank depend on notebooks or manual scripts.
- Do not edit the imported reference trees to make the project code work.
- Do not treat the current standalone ILD experiment as a substitute for the full baseline renderer.

## Minimum Done Definition For Phase 02

1. One run resolves assets and builds the front-end bundle.
2. `BSM-LS` and `BSM-MagLS` render through the project-side shared renderer.
3. ILD and GCC-PHAT ITD proxy losses both run on the rendered responses.
   The ITD path must follow the paper-side GCC-PHAT cross-correlation MSE definition.
4. `FCR-Mixer` produces finite `delta_c` and supports backpropagation.
5. One joint optimization run exports metrics and traces against `BSM-MagLS`.

## Immediate Documentation Outcome

- After this refinement pass, every required Phase 02 implementation area is now assigned either:
  - a file-level external anchor that must be wrapped or reproduced, or
  - an explicit design authority inside `20260324_BSM_Neural_Optimization_Plan.md`
- No Phase 02 core module is allowed to remain unspecified between those two sources.
- The execution path is now also bound to active tasks and session-scoped verification through `PROT-03`.
