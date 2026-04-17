---
Document_ID: ARCH-02
Title: Method Pipeline
Status: Draft
Phase: Phase_02_Development
Track: Architecture
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Distillations/DIST-0002_Phase01_Architecture_Baseline.md
  - 01_Charter/Goals/CHAR-06_Phase_01_Execution_Plan.md
  - 02_Architecture/Logic/ARCH-01_Logical_Flow.md
  - 05_Experiments/Registry/EXP-Registry.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Method Pipeline

## Pipeline Intent

- This pipeline expands the logical flow into the ordered processing stages expected in the Phase 01 implementation.

## Pipeline Diagram

```mermaid
graph TD
    S([Start]) --> A[Stage 0 Resolve assets and environment]
    A --> B[Stage 1 Prepare static direction grid]
    B --> C[Stage 2 Build front end bundle]
    C --> D[Stage 3 Render baseline responses]
    C --> E[Stage 4 Assemble solver inputs]
    E --> F[Stage 5 Predict residual coefficients]
    F --> G[Stage 6 Form joint coefficients]
    G --> H[Stage 7 Render joint responses]
    D --> I[Stage 8 Compute baseline metrics]
    H --> J[Stage 9 Compute joint losses and metrics]
    I --> K[Stage 10 Compare against BSM MagLS]
    J --> K
    K --> L{More optimization iterations needed}
    L -->|Yes| F
    L -->|No| M[Stage 11 Store traces and summaries]
    M --> T([End])
```

## Stage Breakdown

### Stage 0. Resolve Assets And Environment

- Validate that the run is inside `bsm_harness_py311`.
- Resolve required external assets such as array transfer functions, KU100 HRIRs, and imported reference data.

### Stage 1. Prepare Static Direction Grid

- Define the Phase 01 direction set for static evaluation.
- Keep the grid deterministic so that baseline and joint methods are directly comparable.

### Stage 2. Build Front-End Bundle

- Produce the semantic bundle used by all later stages:
  - `grid`: static direction coordinates
  - `V`: array-side steering or forward model terms
  - `h`: target binaural transfer responses
  - `c_ls`: least-squares baseline coefficients
  - `c_magls`: magnitude-least-squares baseline coefficients

### Stage 3. Render Baseline Responses

- Render or evaluate the binaural output of `c_ls` and `c_magls`.
- Keep `BSM-MagLS` as the main reference for Phase 01 comparisons.

### Stage 4. Assemble Solver Inputs

- Feed the residual solver with `c_magls` and the accepted condition features.
- Condition features may include frequency index, direction metadata, or front-end descriptors, but they do not change the renderer semantics.

### Stage 5. Predict Residual Coefficients

- Use a residual MLP to produce `Delta c`.
- The prediction target is a correction in coefficient space, not a direct acoustic output.

### Stage 6. Form Joint Coefficients

- Apply the fixed update rule:
  - `c_joint = c_magls + alpha * Delta c`
- `alpha` remains a controlled scalar gate and may be part of ablation studies.

### Stage 7. Render Joint Binaural Responses

- Reuse the same BSM rendering front-end to evaluate `c_joint` on the static direction grid.

### Stage 8. Compute Baseline Reference Metrics

- Produce baseline-side objective summaries to anchor later comparison.

### Stage 9. Compute Joint Losses And Metrics

- Compute the accepted objective family:
  - magnitude mismatch
  - magnitude-derivative mismatch
  - ERB-band ILD mismatch
  - GCC-PHAT-style ITD proxy mismatch
  - residual regularization

### Stage 10. Compare Against `BSM-MagLS`

- Produce delta metrics and direction-wise summaries.
- The acceptance question is whether the joint method closes objective gaps without destabilizing the rendering path.

### Stage 11. Store Traces And Summaries

- Save convergence traces, per-loss values, metric summaries, and artifact references in experiment records.

## Expansion Points Reserved For Later

- Dynamic yaw conditioning
- Additional arrays or HRTFs
- Alternative ITD formulations beyond the initial GCC-PHAT proxy
- Subjective evaluation layers
