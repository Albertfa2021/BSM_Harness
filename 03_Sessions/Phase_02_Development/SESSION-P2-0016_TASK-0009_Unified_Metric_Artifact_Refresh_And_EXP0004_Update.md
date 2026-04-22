---
Document_ID: SESSION-P2-0016
Title: TASK-0009 Unified Metric Artifact Refresh And EXP0004 Update
Status: Stable
Phase: Phase_02_Development
Track: Session
Maturity: Execution
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0015_TASK-0009_ILD_Metric_Unification_And_Energy_Descriptor_Repair.md
Last_Updated: 2026-04-22
Review_Required: Yes
---

# TASK-0009 Unified Metric Artifact Refresh And EXP0004 Update

## Target Subtask

- Refresh historical `TASK-0009` comparison artifacts under the unified ILD metric where compatible.
- Rewrite `EXP-0004` so its thresholds, commands, and interpretation all match the current implementation.

## Runtime Closure

- Updated `EXP-0004`:
  - yaw `0` baseline-to-beat now uses the unified metric:
    - `ild_error = 12.72058527441395`
    - `itd_proxy_error = 0.02620715039960546`
    - `normalized_magnitude_error = 0.47876036643371495`
    - `nmse = 1.3708966970443726`
    - `retained_composite_metric = 14.596449488291642`
  - all screening commands now use:
    - `--max-frequency-bins 513`
  - historical-refresh notes were updated to reflect the current runner behavior
- Refreshed compatible historical `TASK-0009` `comparison_summary.json` files with the unified metric:
  - `T09-I1-y0-s3401`
  - `T09-I2-y0-s3401`
  - `T09-P1-y90-s3401`
  - `T09-P2-y90-s3401`
  - `T09-P3-y90-s3401`
  - `T09-P4-y0-s3401`
  - `T09-P5-y0-s3401`
  - `T09-P6-y0-s3401`
  - `T09-P7-y0-s3401`
  - `T09-P8-y0-s3401`
  - `T09-SM1-y0-s3401`

## Historical Refresh Result

- Under the refreshed unified metric, all compatible historical retained screening runs now beat the baseline on runner composite verdict.
- None of those refreshed historical runs satisfy:
  - `four_down_accept`
  - `paper_like_accept`
- Therefore the refreshed history still does not justify promotion.

## Old-Format Exception

- `T09-I3-y0-s3401` was created before the energy-descriptor plumbing repair.
- Its checkpoint was trained with the old `14`-channel solver input.
- After the repair, the manifest-declared energy-descriptor path expects `15` channels.
- Therefore `T09-I3-y0-s3401` cannot be replayed by the repaired compare path without a compatibility shim.
- Treat `T09-I3-y0-s3401` as a historical pre-repair artifact, not as current comparison authority.

## Immediate Follow-up

- The next authoritative `TASK-0009` step should be a new official rerun under:
  - full `513` frequency bins
  - unified paper-aligned ILD metric
  - repaired energy-descriptor plumbing
- The refreshed historical artifacts are now useful for context, but they are no longer sufficient as the sole promotion basis.
