---
Document_ID: SESSION-P2-0011
Title: TASK-0009 Screening Execution
Status: Stable
Phase: Phase_02_Development
Track: Session
Maturity: Execution
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 05_Experiments/EXP-0003_TASK-0009_Planned_Optimization_Campaign/README.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0010_TASK-0009_Optimization_Planning.md
  - 05_Experiments/Registry/Result_Tracker.md
  - 06_Assets/Generated_Artifacts/Index.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# TASK-0009 Screening Execution

## Target Subtask

- Implement the missing `TASK-0009` runtime features required by `EXP-0003`.
- Execute the first official pilot sweep on the accepted yaw `90` route.
- Record one explicit promotion decision before any long-run job is allowed to start.

## Runtime Closure

- Added `bsm.phase02.task09_runner` with:
  - normalized composite loss support
  - checkpoint save and resume
  - `run_manifest.json`, `loss_trace.jsonl`, `eval_trace.jsonl`, `summary.json`, and `comparison_summary.json`
  - `train` and `compare` CLI entry points
- Regression gate before implementation:
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests`
  - `30` tests passed
- Regression gate after implementation:
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests`
  - `34` tests passed

## Official Pilot Matrix

- `T09-P1-y90-s3401`
  - profile: `balanced_norm_v1`
  - best composite: `0.6823205258271933` at iteration `500`
  - final iteration: `900`
  - stop reason: `early_stop_no_composite_improvement_4`
  - retained verdict: `baseline_not_beaten`
  - artifact root: `06_Assets/Generated_Artifacts/TASK-0009/T09-P1-y90-s3401/`
- `T09-P2-y90-s3401`
  - profile: `spatial_norm_v1`
  - best composite: `0.48728510709982803` at iteration `1200`
  - final iteration: `1200`
  - stop reason: `max_iterations_reached`
  - retained verdict: `baseline_not_beaten`
  - artifact root: `06_Assets/Generated_Artifacts/TASK-0009/T09-P2-y90-s3401/`
- `T09-P3-y90-s3401`
  - profile: `fidelity_norm_v1`
  - best composite: `0.5424434824380371` at iteration `1200`
  - final iteration: `1200`
  - stop reason: `max_iterations_reached`
  - retained verdict: `baseline_not_beaten`
  - artifact root: `06_Assets/Generated_Artifacts/TASK-0009/T09-P3-y90-s3401/`

## Screening Result

- Pilot ranking by declared composite score:
  - `T09-P2-y90-s3401`
  - `T09-P3-y90-s3401`
  - `T09-P1-y90-s3401`
- All three pilot runs produced machine-readable checkpoint, trace, summary, and comparison artifacts.
- All three retained checkpoints improved normalized magnitude error relative to the static baseline, but none beat `BSM-MagLS` / saved aligned-ypr eMagLS on the required comparison verdict because ILD error remained worse than baseline.

## Promotion Decision

- Decision: `no_promotion`
- Reason:
  - the screening winner was `spatial_norm_v1`
  - however, the retained checkpoint comparison for `T09-P2-y90-s3401` still recorded `baseline_not_beaten`
  - the first official `TASK-0009` session therefore did not justify launching `T09-R1-y90-s3401`
- Result:
  - no `8000`-iteration promoted long run was executed in this session
  - `TASK-0009` remains active

## Continuation Recommendation

- Keep the accepted `TASK-0008` yaw `90` route unchanged.
- Treat the first official screening matrix as complete and reproducible.
- Use the next `TASK-0009` session to diagnose why the normalized-loss winner improves magnitude/NMSE while still regressing ILD relative to baseline.
- If that tradeoff cannot be repaired with a narrow loss-policy adjustment, open a blocker instead of forcing a long-run optimization.
- The owner decision between:
  - extending the `T09-P2-y90-s3401` profile
  - adjusting the loss policy narrowly
  - opening a blocker
  is intentionally deferred to the next session.
