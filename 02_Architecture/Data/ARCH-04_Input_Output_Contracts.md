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
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Input Output Contracts

## Contract Principle

- Contracts are defined at the semantic level so that implementation can change without breaking experiment traceability.

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
