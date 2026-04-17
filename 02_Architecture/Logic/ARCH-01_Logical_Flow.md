---
Document_ID: ARCH-01
Title: Logical Flow
Status: Draft
Phase: Phase_02_Development
Track: Architecture
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Distillations/DIST-0002_Phase01_Architecture_Baseline.md
  - 01_Charter/Goals/CHAR-06_Phase_01_Execution_Plan.md
  - 02_Architecture/Logic/ARCH-02_Method_Pipeline.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Logical Flow

## Scope

- This logical flow fixes the accepted Phase 01 system for static, single-instance neural optimization of BSM coefficients.
- The flow assumes `Easycom + KU100`, a verified `bsm_harness_py311` environment, and a reusable BSM rendering front-end.

## System Flow

```mermaid
flowchart TD
    S([Start]) --> A[Resolve assets and environment]
    A --> B[Build unified front-end]
    B --> C[Produce front-end bundle<br/>direction grid, V, h, c_ls, c_magls]
    C --> D[Render baselines<br/>BSM-LS and BSM-MagLS]
    C --> E[Assemble residual-solver inputs]
    E --> F[Predict Delta c with residual MLP]
    F --> G[Compose joint coefficients<br/>c_joint = c_magls + alpha * Delta c]
    G --> H[Render joint binaural responses]
    D --> I[Collect baseline outputs]
    H --> J[Collect joint outputs]
    I --> K[Evaluate metrics and losses]
    J --> K
    K --> L{Optimization converged?}
    L -->|No| F
    L -->|Yes| M[Export objective metrics<br/>ILD error, ITD proxy error, normalized magnitude error, NMSE]
    M --> N[Register experiment traces and artifacts]
    N --> T([End])
```

## Accepted Logic Layers

### 1. Asset And Environment Layer

- Resolve the external assets and dependency environment needed to reproduce the front-end and evaluation path.
- Treat imported open-source trees as read-only references.

### 2. Front-End Preparation Layer

- Build a unified front-end interface that exposes the core objects required downstream:
  - direction grid
  - array steering or rendering object `V`
  - target binaural response `h`
  - baseline coefficients `c_ls` and `c_magls`

### 3. Baseline Layer

- Reproduce `BSM-LS` and `BSM-MagLS` as objective baselines.
- Use `c_magls` as the default initializer for the learned residual path.

### 4. Learned Residual Layer

- The neural model operates in coefficient space only.
- It predicts `Delta c`, not binaural waveforms.
- The accepted update rule is `c_joint = c_magls + alpha * Delta c`.

### 5. Rendering And Loss Layer

- Render binaural outputs through the same BSM front-end used by the baselines.
- Compute the accepted Phase 01 objectives:
  - binaural magnitude error
  - binaural magnitude-derivative error
  - ERB-band ILD error
  - GCC-PHAT-style ITD proxy error
  - residual-size and smoothness regularization

### 6. Evaluation Closure Layer

- Compare the joint method against `BSM-MagLS` on static direction sets.
- Export objective summaries and optimization traces before any subjective stage is considered.

## Fixed Non-Goals In This Flow

- No end-to-end waveform predictor replaces the renderer.
- No dynamic yaw trajectory optimization is required in Phase 01.
- No multi-array generalization is assumed.
- No subjective listening workflow is part of the accepted core loop.
