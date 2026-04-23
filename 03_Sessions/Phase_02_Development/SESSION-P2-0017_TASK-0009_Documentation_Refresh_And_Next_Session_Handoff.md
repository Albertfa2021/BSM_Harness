---
Document_ID: SESSION-P2-0017
Title: TASK-0009 Documentation Refresh And Next Session Handoff
Status: Stable
Phase: Phase_02_Development
Track: Session
Maturity: Planning
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 00_Governance/Manifest/MANI-00_Project_State.md
  - 00_Governance/Manifest/MANI-02_Active_Focus.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0014_TASK-0009_Baseline_Not_Beaten_Diagnosis_And_Repair_Plan.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0015_TASK-0009_ILD_Metric_Unification_And_Energy_Descriptor_Repair.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0016_TASK-0009_Unified_Metric_Artifact_Refresh_And_EXP0004_Update.md
Last_Updated: 2026-04-22
Review_Required: Yes
---

# TASK-0009 Documentation Refresh And Next Session Handoff

## Target Subtask

- Refresh the project document system so the next session can continue `TASK-0009` without reconstructing the repaired metric/plumbing state by hand.
- Record the current authoritative next step after `SESSION-P2-0016`.

## Current Authority Snapshot

- `TASK-0009` optimization and comparison authority is now full-frequency `513`.
- ILD training loss and exported ILD evaluation now use the same paper-aligned banded metric family.
- `--include-front-end-energy-descriptor` is now real plumbing rather than a fake ablation flag.
- `EXP-0004` now carries the authoritative yaw `0` baseline and acceptance thresholds under the unified metric.
- Compatible historical retained runs have already been refreshed under the unified metric.

## Current Result Boundary

- Refreshed historical retained runs are useful context, but none of them satisfy:
  - `four_down_accept`
  - `paper_like_accept`
- Therefore the official decision remains:
  - `no_promotion`
- `T09-I3-y0-s3401` remains a pre-repair old-format artifact because its checkpoint expects the old `14`-channel solver input while the repaired energy-descriptor path expects `15`.

## Required Next Session Starting Point

- Start from `MANI-03`, `TASK-0009`, and `EXP-0004`.
- Do not spend the next session re-diagnosing the old metric mismatch or the old energy-descriptor bug; both are already closed in code and documented.
- The next engineering action should be a new official `TASK-0009` rerun under:
  - full `513` bins
  - unified paper-aligned ILD metric
  - repaired energy-descriptor plumbing
- Promotion should still remain blocked unless the new retained run reaches at least `paper_like_accept`.

## Documentation Closure

- Governance manifests and task/session indexes were refreshed in this session so the new continuation chain points at the repaired state and the next-session handoff.
