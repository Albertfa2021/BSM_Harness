---
Document_ID: SESSION-P2-0020
Title: TASK-0009 Post Promotion Yaw0 NMSE Followup Execution
Status: Stable
Phase: Phase_02_Development
Track: Session
Maturity: Execution
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 00_Governance/Manifest/MANI-00_Project_State.md
  - 00_Governance/Manifest/MANI-02_Active_Focus.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0018_TASK-0009_Official_Full513_Rerun_And_Promotion.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0019_TASK-0009_Promoted_Yaw0_NMSE_Gap_Closure_Handoff.md
  - 05_Experiments/Registry/Result_Tracker.md
  - 06_Assets/Generated_Artifacts/Index.md
Last_Updated: 2026-04-23
Review_Required: Yes
---

# TASK-0009 Post Promotion Yaw0 NMSE Followup Execution

## Target Subtask

- Start from `MANI-03`, `SESSION-P2-0018`, `SESSION-P2-0019`, `TASK-0009`, and `EXP-0004`.
- Re-run the regression gate before new execution.
- Keep the promoted yaw `0` route fixed as the authority baseline:
  - `paper_ild_push_v1`
  - `hidden_dim = 48`
  - `block_count = 3`
  - `rank = 8`
  - `alpha_init = 0.15`
  - `alpha_max = 0.35`
  - full `513` bins
  - unified paper-aligned ILD metric
- Run only a narrow comparison batch and do not authorize a new long run unless the retained evidence clearly improves on `T09-R2-y0-s3401`.

## Runtime Closure

- Regression gate:
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests`
  - result:
    - `39` tests passed
- Updated `bsm.phase02.task09_runner` so this session records:
  - `producer_session_id = SESSION-P2-0020`
- Added two late-stage near-promoted loss profiles for narrow testing only:
  - `paper_ild_push_v1_late_mag_guard`
  - `paper_ild_push_v1_late_dmag_guard`

## Narrow Comparison Batch

- Batch artifact:
  - `06_Assets/Generated_Artifacts/TASK-0009/yaw0_nmse_followup_SESSION-P2-0020_y0_s3401/comparison_summary.json`
- Comparison authorities used:
  - `EXP-0004` baseline
  - promoted authority `T09-R2-y0-s3401`

### Run Matrix

- `T09-N1-y0-s3401`
  - profile: `paper_ild_push_v1`
  - note: short-horizon control at `1400` iterations; this is not a strict replay of `T09-R2` iterations `0-1400` because warmup/final stage boundaries scale with total iterations
- `T09-N2-y0-s3401`
  - profile: `paper_ild_push_v1_late_mag_guard`
  - intent: lightly restore late `mag` pressure while keeping the promoted capacity unchanged
- `T09-N3-y0-s3401`
  - profile: `paper_ild_push_v1_late_dmag_guard`
  - intent: lightly restore late `dmag` protection while keeping the promoted capacity unchanged

### Retained Results

- `T09-N1-y0-s3401`
  - retained composite: `5.785742196888973`
  - retained metrics:
    - `ild_error = 3.984675935359572`
    - `itd_proxy_error = 0.017995407543119117`
    - `normalized_magnitude_error = 0.33084445361091464`
    - `nmse = 1.4522264003753662`
  - acceptance: `reject`
- `T09-N2-y0-s3401`
  - retained composite: `5.814385666065418`
  - retained metrics:
    - `ild_error = 3.998519635630442`
    - `itd_proxy_error = 0.01834493776105863`
    - `normalized_magnitude_error = 0.3234808228222328`
    - `nmse = 1.4740402698516846`
  - acceptance: `reject`
- `T09-N3-y0-s3401`
  - retained composite: `5.803081807186033`
  - retained metrics:
    - `ild_error = 4.009099687502574`
    - `itd_proxy_error = 0.01862626579345248`
    - `normalized_magnitude_error = 0.33307532296044173`
    - `nmse = 1.4422805309295654`
  - acceptance: `paper_like_accept`

### Comparison Against The Promoted Authority

- `T09-R2-y0-s3401` retained metrics remain:
  - `ild_error = 1.7256287218571187`
  - `itd_proxy_error = 0.016510563573170753`
  - `normalized_magnitude_error = 0.30524950299696796`
  - `nmse = 1.3829925060272217`
- All three narrow retained runs stayed above the promoted authority on:
  - `nmse`
  - retained composite
  - ILD
  - magnitude
- Best narrow retained `nmse`:
  - `T09-N3-y0-s3401 = 1.4422805309295654`
  - delta vs promoted authority:
    - `+0.05928802490234375`
- No narrow retained run reached `four_down_accept`.

## Important Trace Observation

- `T09-R2-y0-s3401` evaluation trace shows a transient `four_down_accept` window at iterations:
  - `800`
  - `1000`
  - `1200`
  - `1400`
- Example early retained-quality point from the promoted trace:
  - iteration `800`
  - `ild_error = 3.634389020177412`
  - `itd_proxy_error = 0.017936094654027315`
  - `normalized_magnitude_error = 0.37568440887148885`
  - `nmse = 1.321073293685913`
- However:
  - those earlier evaluation points were not preserved as separate archived checkpoints
  - the retained `best_composite` checkpoint later drifted past that window
  - this session therefore does not treat the trace observation alone as sufficient to authorize a fresh long run

## Session Decision

- Official result:
  - `no_new_long_run`
- Interpretation:
  - the narrow batch did not close the retained yaw `0` `nmse` gap
  - the promoted authority remains `T09-R2-y0-s3401`
  - `four_down_accept` remains unmet

## Continuation Recommendation

- Keep `T09-R2-y0-s3401` as the promoted yaw `0` authority.
- Preserve the new narrow follow-up artifacts:
  - `T09-N1-y0-s3401`
  - `T09-N2-y0-s3401`
  - `T09-N3-y0-s3401`
  - `yaw0_nmse_followup_SESSION-P2-0020_y0_s3401/comparison_summary.json`
- Do not launch another yaw `0` long run from this batch.
- The next owner decision can now move to the documented fallback priorities:
  - transfer the promoted non-energy-descriptor configuration to yaw `90`
  - or separately judge whether the repaired energy-descriptor route deserves its own long run
