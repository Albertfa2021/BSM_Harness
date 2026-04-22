---
Document_ID: EXP-0003
Title: TASK-0009 Planned Optimization Campaign
Status: Draft
Phase: Phase_02_Development
Track: Experiment
Maturity: Planning
Related_Docs:
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0010_TASK-0009_Optimization_Planning.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0009_Orientation_Training_Path_Smoke.md
  - 02_Architecture/Logic/ARCH-09_Planned_Optimization_Campaign_Blueprint.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 05_Experiments/Registry/EXP-Registry.md
  - 06_Assets/Generated_Artifacts/Index.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# TASK-0009 Planned Optimization Campaign

## Purpose

- Define the next executable session protocol for `TASK-0009`.
- Fix the first official screening matrix, shortlist policy, promotion policy, and logging policy before long-run optimization starts.

## Required Runtime

```bash
conda activate bsm_harness_py311
```

Or run every command through:

```bash
conda run -n bsm_harness_py311 <command>
```

## Starting Authority

- Inherited route authority:
  - `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/`
- Selected first optimization orientation:
  - yaw `90`
- Current accepted smoke result:
  - `initial_loss_total = 3.4457359313964844`
  - `final_loss_total = 3.0254967212677`
  - `loss_reduced = true`

## Mandatory Implementation Additions Before The First Formal Run

The next execution session must first add the smallest missing `TASK-0009` runtime features:

1. Normalized composite loss support.
2. Checkpoint save and resume.
3. Structured run manifest and streaming log writers.
4. Evaluation trace and comparison summary export.

Preferred command shape:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train ...
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner compare ...
```

If the implementation chooses a different CLI shape, it must still produce the same artifacts and metadata defined below.

## Loss Policy

### Raw Loss Terms

- `loss_mag`
- `loss_dmag`
- `loss_ild`
- `loss_itd`
- `loss_reg`

### Normalization Rule

- During warmup, estimate a frozen reference scale for each loss term using an EMA or equivalent stable mean.
- Use the normalized objective after warmup:

```text
loss_total_norm = sum(lambda_i * (loss_i / scale_i))
```

Where:

- `scale_i = max(warmup_reference_i, eps)`
- `eps` must prevent divide-by-zero

### Official Weight Schedules

`balanced_norm_v1`

- warmup:
  - `mag = 0.40`
  - `dmag = 0.25`
  - `ild = 0.20`
  - `itd = 0.10`
  - `reg = 0.05`
- main:
  - `mag = 0.30`
  - `dmag = 0.20`
  - `ild = 0.25`
  - `itd = 0.20`
  - `reg = 0.05`
- final:
  - `mag = 0.25`
  - `dmag = 0.15`
  - `ild = 0.30`
  - `itd = 0.25`
  - `reg = 0.05`

`spatial_norm_v1`

- warmup:
  - `mag = 0.35`
  - `dmag = 0.20`
  - `ild = 0.25`
  - `itd = 0.15`
  - `reg = 0.05`
- main:
  - `mag = 0.20`
  - `dmag = 0.15`
  - `ild = 0.35`
  - `itd = 0.25`
  - `reg = 0.05`
- final:
  - `mag = 0.15`
  - `dmag = 0.10`
  - `ild = 0.40`
  - `itd = 0.30`
  - `reg = 0.05`

`fidelity_norm_v1`

- warmup:
  - `mag = 0.45`
  - `dmag = 0.25`
  - `ild = 0.15`
  - `itd = 0.10`
  - `reg = 0.05`
- main:
  - `mag = 0.40`
  - `dmag = 0.25`
  - `ild = 0.20`
  - `itd = 0.10`
  - `reg = 0.05`
- final:
  - `mag = 0.35`
  - `dmag = 0.20`
  - `ild = 0.25`
  - `itd = 0.15`
  - `reg = 0.05`

## Runtime Management Policy

### Stage A. Regression Gate

Run before any implementation or optimization execution:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

### Stage B. Pilot Sweep

Purpose:

- eliminate bad schedules cheaply and identify a shortlist worth promoting

Pilot matrix:

| Run ID | Orientation | Seed | Loss Profile | Max Frequency Bins | Iterations | Eval Every | Checkpoint Every |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `T09-P1-y90-s3401` | yaw `90` | `3401` | `balanced_norm_v1` | `129` | `1200` | `100` | `200` |
| `T09-P2-y90-s3401` | yaw `90` | `3401` | `spatial_norm_v1` | `129` | `1200` | `100` | `200` |
| `T09-P3-y90-s3401` | yaw `90` | `3401` | `fidelity_norm_v1` | `129` | `1200` | `100` | `200` |

Early-stop rule:

- stop a pilot if no improvement in composite validation score is observed for `4` consecutive evaluation windows

Promotion rule:

- rank pilot runs by declared composite validation score
- promote only the best profile if it is clearly acceptable
- otherwise record `no_promotion` and stop after screening

### Stage C. Promoted Long Run

Purpose:

- run a true long optimization only for a profile that earned promotion in screening

Promoted run policy:

- promote only the best pilot profile
- keep yaw `90` as the primary retained run
- restore full frequency resolution
- do not launch multiple long runs in parallel as part of the first official `TASK-0009` session

Promoted run default:

| Run ID | Orientation | Seed | Loss Profile | Max Frequency Bins | Iterations | Eval Every | Checkpoint Every |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `T09-R1-y90-s3401` | yaw `90` | `3401` | best pilot profile | full `513` | `8000` | `200` | `500` |

Early-stop rule:

- stop if no improvement in retained composite validation score is observed for `8` consecutive evaluation windows

### Stage D. Optional Control Run

- yaw `0` is not part of the required first retained result
- if time permits, add exactly one control run:
  - `T09-C1-y0-s3401`

## Host Power And Sleep Policy

- Do not make an authoritative promoted long run depend on an operating-system experimental feature that claims to keep processes running while the machine sleeps.
- Preferred execution policy:
  - AC power connected
  - screen sleep allowed
  - system sleep disabled during the promoted long run
- If the operator still chooses to use an experimental sleep-continue feature:
  - record `power_mode = experimental_sleep_continue` in `run_manifest.json`
  - verify wall-clock continuity and checkpoint integrity after wake
  - if continuity is suspicious, resume from `checkpoints/last.pt` and record the interruption explicitly

## Logging And Artifact Policy

Required artifact root:

```text
06_Assets/Generated_Artifacts/TASK-0009/<run_id>/
```

Required files:

```text
run_manifest.json
summary.json
loss_trace.jsonl
eval_trace.jsonl
comparison_summary.json
checkpoints/
  last.pt
  best_loss.pt
  best_composite.pt
```

### `run_manifest.json`

Must record:

- `schema_version`
- `interface_version`
- `producer_task_id = TASK-0009`
- `producer_session_id`
- `run_config_ref`
- `run_id`
- `orientation_yaw_deg`
- `seed`
- `optimizer`
- `learning_rate`
- `loss_profile`
- normalized-loss policy
- checkpoint cadence
- evaluation cadence
- artifact root
- environment name
- `power_mode`
- `sleep_policy_note`

### `loss_trace.jsonl`

One line per optimization iteration. Minimum fields:

- `iteration`
- `wall_time_sec`
- `learning_rate`
- `alpha`
- `loss_total`
- `loss_mag`
- `loss_dmag`
- `loss_ild`
- `loss_itd`
- `loss_reg`
- `residual_norm`
- `grad_norm`, if available

### `eval_trace.jsonl`

One line per evaluation event. Minimum fields:

- `iteration`
- `checkpoint_ref`
- `validation_score_composite`
- `ild_error`
- `itd_proxy_error`
- `normalized_magnitude_error`
- `nmse`
- `retained_best_loss`
- `retained_best_composite`

### `summary.json`

Must be updated during execution and finalized at the end. Minimum fields:

- manifest reference
- best checkpoint references
- selected retained criterion
- best iteration
- final iteration
- stop reason
- retained metric summary

### `comparison_summary.json`

Must compare the retained checkpoint against:

- `BSM-MagLS`
- saved aligned-ypr eMagLS reference

Minimum fields:

- retained run id
- retained checkpoint
- comparison baselines
- ILD error
- ITD proxy error
- normalized magnitude error
- NMSE
- concise retention verdict

## Session Execution Order

1. Run the regression gate.
2. Implement missing `TASK-0009` runner features.
3. Add or update tests for:
   - normalized loss handling
   - checkpoint write and resume
   - manifest and trace export
4. Rerun the regression gate.
5. Execute the three pilot runs.
6. Record the promotion decision in the session note.
7. If promotion is granted, execute the promoted long run.
8. If a long run happened, export `comparison_summary.json`.
9. Update:
   - `SESSION-P2-0010` or the new execution session note
   - `05_Experiments/Registry/Result_Tracker.md`
   - `06_Assets/Generated_Artifacts/Index.md`
   - manifests, if focus changes

## Acceptance

- The experiment is successful only if:
  - regression passes before and after implementation
  - all pilot runs complete or early-stop cleanly
  - one explicit promotion decision is recorded
  - required artifact files exist
  - checkpoint resume works
  - if a long run happens, `comparison_summary.json` exists
- If these checks fail:
  - keep `TASK-0009` active
  - record the blocker in the next execution session note
  - do not claim formal optimization closure
