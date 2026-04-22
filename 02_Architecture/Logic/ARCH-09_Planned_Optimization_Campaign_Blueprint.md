---
Document_ID: ARCH-09
Title: Planned Optimization Campaign Blueprint
Status: Draft
Phase: Phase_02_Development
Track: Architecture
Maturity: Planning
Related_Docs:
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 05_Experiments/EXP-0003_TASK-0009_Planned_Optimization_Campaign/README.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0010_TASK-0009_Optimization_Planning.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# Planned Optimization Campaign Blueprint

## Purpose

- Define the execution blueprint for `TASK-0009`.
- Fix the difference between the accepted `TASK-0008` smoke route and the first formal long-run optimization campaign.

## Design Principle

- `TASK-0009` inherits the accepted `TASK-0008` route and must not redesign it during routine execution.
- `TASK-0009` adds campaign structure:
  - normalized composite loss handling
  - screening-first run matrix
  - checkpoint and resume
  - structured logging
  - promotion-based comparison

## Execution Flow

### Step 1. Freeze Route Authority

- Use the accepted orientation-aware route from `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/`.
- Selected orientation for the first official campaign is yaw `90`.
- yaw `0` may appear only as an explicit control run.

### Step 2. Build Normalized Composite Loss

- Raw loss terms remain:
  - `loss_mag`
  - `loss_dmag`
  - `loss_ild`
  - `loss_itd`
  - `loss_reg`
- Formal optimization must not rely on static raw-term weights alone, because term magnitudes differ strongly.
- The campaign should compute frozen reference scales during warmup:
  - `scale_i = max(warmup_ema(loss_i), eps)`
- Main optimization should use:

```text
loss_total_norm = sum(lambda_i * (loss_i / scale_i))
```

### Step 3. Use A Three-Stage Weight Schedule

- Warmup stage:
  - `mag = 0.40`
  - `dmag = 0.25`
  - `ild = 0.20`
  - `itd = 0.10`
  - `reg = 0.05`
- Main stage:
  - `mag = 0.30`
  - `dmag = 0.20`
  - `ild = 0.25`
  - `itd = 0.20`
  - `reg = 0.05`
- Final stage:
  - `mag = 0.25`
  - `dmag = 0.15`
  - `ild = 0.30`
  - `itd = 0.25`
  - `reg = 0.05`

## Step 4. Stage Runtime Cost Deliberately

- Formal execution must be staged:
  - pilot sweep
  - promotion decision
  - optional promoted long run
- Pilot sweep exists to eliminate bad schedules cheaply.
- A long run is executed only if the screening result justifies promotion.

### Pilot Sweep Policy

- Use yaw `90` only.
- Use reduced frequency count for screening.
- Keep the run matrix narrow:
  - `balanced_norm_v1`
  - `spatial_norm_v1`
  - `fidelity_norm_v1`
- The pilot sweep is the main purpose of the first `TASK-0009` execution session.
- Do not expand into broad combinatorial trials in the first official campaign.

### Promotion Policy

- Screening must end with an explicit promotion decision.
- Promote only the best pilot profile.
- If no pilot profile is clearly acceptable, record `no_promotion` and stop instead of forcing a long run.

### Promoted Long-Run Policy

- A promoted long run restores full frequency resolution.
- A promoted long run requires checkpoint resume and structured evaluation output.
- The first official campaign should run at most one promoted long-run job unless a blocker forces a rerun.

## Step 5. Promote By Validation Score, Not Training Loss Alone

- Each evaluation point must record:
  - normalized composite validation loss
  - ILD error
  - ITD proxy error
  - normalized magnitude error
  - NMSE
- Promotion must be decided by a declared validation score.
- The first campaign should keep this simple:
  - use `best_composite` as the promotion criterion
  - also save `best_loss` for diagnosis

## Step 6. Structured Logging

- Every run must emit:
  - `run_manifest.json`
  - `loss_trace.jsonl`
  - `eval_trace.jsonl`
  - `summary.json`
  - `comparison_summary.json`
  - `checkpoints/`
- Logging must be append-safe and machine-readable.
- Continuation by docs alone must be possible from these artifacts.

## Step 6A. Host Power Policy

- Authoritative long runs must not depend on an OS-level experimental "continue running while asleep" feature.
- Preferred policy:
  - keep the machine on AC power
  - allow the display to sleep if desired
  - disable system sleep for the duration of any promoted long run
- If the operator still uses an experimental sleep-continue feature:
  - record that fact in `run_manifest.json`
  - verify timestamps and checkpoint continuity after wake
  - resume only from the last known-good checkpoint if continuity is questionable

## Step 7. Session Success Condition

- The next `TASK-0009` execution session succeeds only if:
  - the implementation adds normalized-loss, checkpoint, and logging support
  - the pilot sweep completes
  - one explicit promotion decision is recorded
  - if a long run is promoted, it has machine-readable comparison output against declared baselines
