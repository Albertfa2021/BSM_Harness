---
Document_ID: ARCH-03
Title: Data Schema
Status: Draft
Phase: Phase_02_Development
Track: Architecture
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Distillations/DIST-0002_Phase01_Architecture_Baseline.md
  - 01_Charter/Goals/CHAR-06_Phase_01_Execution_Plan.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 06_Assets/Datasets/Index.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Data Schema

## Schema Rule

- This schema fixes semantic objects and axis meaning for Phase 01.
- Concrete in-memory tensor order may vary in implementation, but semantic axes must remain traceable.
- Cross-session handoff objects must reuse the canonical names in this document instead of inventing local aliases.

## Core Semantic Axes

- `d`: direction index on the static evaluation grid
- `f`: frequency bin index
- `m`: array or rendering coefficient index
- `e`: ear index in `{left, right}`
- `t`: time or lag index
- `b`: auditory ERB band index

## Cross-Session Naming Rules

- Public object names used across sessions, modules, tests, and artifacts must reuse the schema names here.
- Local scratch variables such as `x`, `tmp`, `arr`, `foo`, or `out` are acceptable only inside a short local scope.
- They must never be promoted into:
  - module interfaces
  - saved artifacts
  - session handoff notes
  - smoke-test outputs

## Canonical Suffix Rules

- Use these suffixes when naming derived objects:
  - `_ls`: least-squares baseline
  - `_magls`: magnitude-least-squares baseline
  - `_joint`: learned or composed joint variant
  - `_ref`: reference target
  - `_est`: estimated or rendered candidate
  - `_init`: initialization value
  - `_trace`: iteration-wise log or sequence
  - `_summary`: aggregated export or report
- Use `delta_` prefix for learned corrections such as `delta_c`.
- Use explicit unit suffixes for scalar arrays and config values:
  - `_hz`
  - `_deg`
  - `_samples`
  - `_db`

## Complex Value Rule

- If a tensor is conceptually complex and the implementation can preserve a complex dtype, keep the canonical complex object name, for example `c_magls`.
- If a complex tensor must be split into real channels for a model or export, name the split fields explicitly:
  - `<name>_re`
  - `<name>_im`
- Do not overload a real-valued packed tensor with the same name as the complex semantic object without documenting the packing step.

## Session Handoff Metadata Rule

- Any saved object intended for reuse in a later session must carry or be accompanied by:
  - `schema_version`
  - `producer_task_id`
  - `producer_session_id`
  - `run_config_ref`
- This metadata can live inside the object or in an adjacent manifest file, but it must exist before another session treats the output as authoritative.

## Core Objects

### 1. Asset Bundle

- Purpose: resolved external resources required for a run
- Required fields:
  - `array_id`
  - `hrtf_id`
  - `device_atf_path`
  - `array_sh_path` or equivalent front-end asset path
  - `hrir_path`
  - `environment_name`

### 2. Direction Grid

- Purpose: stable list of static evaluation directions
- Required fields:
  - `azimuth_deg[d]`
  - `elevation_deg[d]`
  - optional `metadata[d]`

### 3. Front-End Bundle

- Purpose: shared input package for baselines, solver, renderer, and evaluator
- Required fields:
  - `grid`
  - `V[d, f, m]` or equivalent semantic steering object
  - `h[d, f, e]` target binaural response
  - `c_ls[f, m, e]`
  - `c_magls[f, m, e]`
  - optional auxiliary descriptors for conditioning

### 4. Residual Solver Input

- Purpose: model-side input for coefficient correction
- Required fields:
  - `c_magls[f, m, e]`
  - optional front-end descriptors
  - optional frequency and direction conditioning

### 5. Residual Output

- Purpose: learned coefficient correction
- Required fields:
  - `delta_c[f, m, e]`
  - optional gate parameter `alpha`

### 6. Joint Coefficient Set

- Purpose: coefficient set passed to rendering
- Required fields:
  - `c_joint[f, m, e]`
- Definition:
  - `c_joint = c_magls + alpha * delta_c`

### 7. Rendered Binaural Response

- Purpose: predicted or baseline binaural output on the direction grid
- Required fields:
  - `response[d, f, e]`
- Variants:
  - `response_ls`
  - `response_magls`
  - `response_joint`

### 8. Auditory ILD Representation

- Purpose: ERB-band spatial cue representation for loss and evaluation
- Required fields:
  - `erb_center_freq_hz[b]`
  - `ild_ref[b, d]`
  - `ild_est[b, d]`

### 9. ITD Proxy Representation

- Purpose: differentiable binaural timing representation
- Required fields:
  - `gcc_phat_ref[d, t]` or semantically equivalent low-frequency timing proxy
  - `gcc_phat_est[d, t]`

### 10. Loss Breakdown

- Purpose: normalized optimization accounting
- Required fields:
  - `loss_mag`
  - `loss_mag_derivative`
  - `loss_ild`
  - `loss_itd`
  - `loss_reg`
  - `loss_total`

### 11. Evaluation Summary

- Purpose: exported experiment-level comparison record
- Required fields:
  - `ild_error`
  - `itd_proxy_error`
  - `normalized_magnitude_error`
  - `nmse`
  - `baseline_name`
  - `run_config_ref`

## Phase 01 Invariants

- `array_id` is fixed to `Easycom`.
- `hrtf_id` is fixed to `KU100`.
- Head orientation is static for the accepted Phase 01 loop.
- `c_magls` is the mandatory initialization point for the learned branch.
