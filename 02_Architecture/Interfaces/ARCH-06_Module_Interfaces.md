---
Document_ID: ARCH-06
Title: Module Interfaces
Status: Draft
Phase: Phase_02_Development
Track: Architecture
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Distillations/DIST-0002_Phase01_Architecture_Baseline.md
  - 01_Charter/Goals/CHAR-06_Phase_01_Execution_Plan.md
  - 01_Charter/Goals/20260324_BSM_Neural_Optimization_Plan.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Module Interfaces

## Interface Goal

- Define the stable module boundaries of the Phase 01 system without forcing a premature final code layout.

## Accepted Module Set

### 1. Asset And Environment Module

- Responsibility:
  - resolve external files and environment assumptions
  - provide validated asset references
- Reference anchor:
  - `Array2Binaural/README.md`
  - `DEP-0001_Array2Binaural_Conda_Env.md`
- Must not:
  - contain learned-model logic
  - mutate imported reference trees

### 2. Front-End Module

- Responsibility:
  - construct the reusable BSM-side bundle
  - expose `V`, `h`, `c_ls`, and `c_magls`
- Reference anchor:
  - `Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py`
- Consumers:
  - baseline renderer
  - residual solver input builder
  - joint renderer
  - evaluator

### 3. Baseline Module

- Responsibility:
  - reproduce `BSM-LS` and `BSM-MagLS`
  - expose baseline coefficients and baseline binaural outputs
- Reference anchor:
  - `Array2Binaural/compute_emagls_filters/compute_emagls2_for_rotations.py`
- Dependency boundary:
  - may depend on the front-end module
  - must not depend on the learned solver

### 4. Residual Solver Module

- Responsibility:
  - map accepted solver inputs to `delta_c`
  - support gated update via `alpha`
- Design authority when no direct external reference exists:
  - `20260324_BSM_Neural_Optimization_Plan.md` Section 四 to Section 六
- Dependency boundary:
  - may consume front-end descriptors
  - must not bypass rendering by outputting binaural signals

### 5. Renderer Module

- Responsibility:
  - render binaural responses from a coefficient set using the shared BSM front-end semantics
- Reference anchor:
  - `Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py`
- Dependency boundary:
  - shared by baseline and learned branches

### 6. Auditory Cue Module

- Responsibility:
  - compute ERB-band ILD representations
  - compute differentiable ITD proxy representations
- Reference anchor:
  - ILD: `BAS-0002` and `EXP-0001_Auditory_ILD_Python`
  - ITD: `Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf`
- Current status:
  - the ILD auditory path has an initial Python replication under `05_Experiments/EXP-0001_Auditory_ILD_Python/`

### 7. Loss Module

- Responsibility:
  - aggregate magnitude, derivative, ILD, ITD, and regularization losses
- Design authority when no direct external reference exists:
  - `20260324_BSM_Neural_Optimization_Plan.md` Section 六
- Dependency boundary:
  - consumes outputs from renderer and auditory cue module
  - returns a structured loss breakdown

### 8. Evaluation Module

- Responsibility:
  - compare baseline and joint outputs
  - export objective metrics and summaries
  - connect runs to experiment records
- Design authority when no direct external reference exists:
  - `20260324_BSM_Neural_Optimization_Plan.md` Section 七

## Interface Rules

- The front-end bundle is the canonical handoff object between upstream preparation and downstream learning or evaluation.
- `c_magls` is the canonical initialization handoff from baseline module to residual solver.
- The renderer interface must be identical for baseline coefficients and joint coefficients.
- Auditory cue analysis is an evaluation and loss dependency, not an alternative rendering path.
- Logging and artifact generation happen after evaluation, not inside the solver core.
