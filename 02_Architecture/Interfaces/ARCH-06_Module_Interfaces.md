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
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
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
- Must not:
  - contain learned-model logic
  - mutate imported reference trees

### 2. Front-End Module

- Responsibility:
  - construct the reusable BSM-side bundle
  - expose `V`, `h`, `c_ls`, and `c_magls`
- Consumers:
  - baseline renderer
  - residual solver input builder
  - joint renderer
  - evaluator

### 3. Baseline Module

- Responsibility:
  - reproduce `BSM-LS` and `BSM-MagLS`
  - expose baseline coefficients and baseline binaural outputs
- Dependency boundary:
  - may depend on the front-end module
  - must not depend on the learned solver

### 4. Residual Solver Module

- Responsibility:
  - map accepted solver inputs to `delta_c`
  - support gated update via `alpha`
- Dependency boundary:
  - may consume front-end descriptors
  - must not bypass rendering by outputting binaural signals

### 5. Renderer Module

- Responsibility:
  - render binaural responses from a coefficient set using the shared BSM front-end semantics
- Dependency boundary:
  - shared by baseline and learned branches

### 6. Auditory Cue Module

- Responsibility:
  - compute ERB-band ILD representations
  - compute differentiable ITD proxy representations
- Current status:
  - the ILD auditory path has an initial Python replication under `05_Experiments/EXP-0001_Auditory_ILD_Python/`

### 7. Loss Module

- Responsibility:
  - aggregate magnitude, derivative, ILD, ITD, and regularization losses
- Dependency boundary:
  - consumes outputs from renderer and auditory cue module
  - returns a structured loss breakdown

### 8. Evaluation Module

- Responsibility:
  - compare baseline and joint outputs
  - export objective metrics and summaries
  - connect runs to experiment records

## Interface Rules

- The front-end bundle is the canonical handoff object between upstream preparation and downstream learning or evaluation.
- `c_magls` is the canonical initialization handoff from baseline module to residual solver.
- The renderer interface must be identical for baseline coefficients and joint coefficients.
- Auditory cue analysis is an evaluation and loss dependency, not an alternative rendering path.
- Logging and artifact generation happen after evaluation, not inside the solver core.
