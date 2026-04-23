---
Document_ID: SESSION-P2-0018
Title: TASK-0009 Official Full513 Rerun And Promotion
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
  - 03_Sessions/Phase_02_Development/SESSION-P2-0017_TASK-0009_Documentation_Refresh_And_Next_Session_Handoff.md
  - 05_Experiments/Registry/Result_Tracker.md
  - 06_Assets/Generated_Artifacts/Index.md
Last_Updated: 2026-04-22
Review_Required: Yes
---

# TASK-0009 Official Full513 Rerun And Promotion

## Target Subtask

- Start from `MANI-03`, `SESSION-P2-0017`, `TASK-0009`, and `EXP-0004`.
- Run the required regression gate before any new official `TASK-0009` execution.
- Launch the new official full-`513` yaw `0` rerun under the unified paper-aligned ILD metric and repaired energy-descriptor plumbing.
- Apply the `EXP-0004` `four_down_accept` / `paper_like_accept` rule, then continue into Stage E and Stage F if promotion becomes justified.

## Runtime Closure

- Updated `bsm.phase02.task09_runner` so new formal `TASK-0009` artifacts record:
  - `producer_session_id = SESSION-P2-0018`
- Regression gate:
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests`
  - result:
    - `39` tests passed

## Official Rerun Batch Summary

- Batch summary artifact:
  - `06_Assets/Generated_Artifacts/TASK-0009/official_full513_rerun_SESSION-P2-0018_y0_s3401_summary.json`
- Baseline authority used from `EXP-0004`:
  - `ild_error = 12.72058527441395`
  - `itd_proxy_error = 0.02620715039960546`
  - `normalized_magnitude_error = 0.47876036643371495`
  - `nmse = 1.3708966970443726`
- `paper_like_accept` authority used from `EXP-0004`:
  - `ild_error <= 11.5`
  - `itd_proxy_error <= 0.029`
  - `normalized_magnitude_error <= 0.52`
  - `nmse <= 1.45`

## Stage C. Official Loss-Policy Screening

- `T09-P9-y0-s3401`
  - profile: `balanced_norm_v1`
  - retained composite: `6.979118486291632`
  - acceptance: `reject`
- `T09-P10-y0-s3401`
  - profile: `spatial_norm_v1`
  - retained composite: `6.779838507348466`
  - acceptance: `reject`
- `T09-P11-y0-s3401`
  - profile: `paper_ild_guarded_v1`
  - retained composite: `6.744143354766082`
  - acceptance: `reject`
- `T09-P12-y0-s3401`
  - profile: `paper_ild_push_v1`
  - retained composite: `6.493929152583029`
  - retained metrics:
    - `ild_error = 4.648010365042856`
    - `itd_proxy_error = 0.02250489050655905`
    - `normalized_magnitude_error = 0.3271073584517669`
    - `nmse = 1.4963065385818481`
  - acceptance: `reject`
- `T09-P13-y0-s3401`
  - profile: `paper_ild_push_v2`
  - retained composite: `6.732206375696253`
  - acceptance: `reject`

Stage C decision:

- winner: `T09-P12-y0-s3401`
- selected profile for Stage D: `paper_ild_push_v1`
- interpretation:
  - under the repaired authority, the best loss profile is no longer `balanced_norm_v1`
  - the strongest Stage C profile already improves ILD / ITD / magnitude strongly, but still fails `paper_like_accept` because `nmse` remains too high

## Stage D. Narrow Initialization / Capacity Screening

- `T09-I4-y0-s3401`
  - solver variant: conservative `alpha_init = 0.05`, `alpha_max = 0.20`
  - retained composite: `6.969252571376294`
  - acceptance: `reject`
- `T09-I5-y0-s3401`
  - solver variant: higher capacity with `hidden_dim = 48`, `block_count = 3`, `rank = 8`
  - retained composite: `5.9319908252053555`
  - retained metrics:
    - `ild_error = 4.133204120406367`
    - `itd_proxy_error = 0.018033743034823795`
    - `normalized_magnitude_error = 0.33803326381189425`
    - `nmse = 1.4427196979522705`
  - acceptance: `paper_like_accept`
- `T09-I6-y0-s3401`
  - solver variant: same higher-capacity setting plus `include_front_end_energy_descriptor = true`
  - retained composite: `6.03331469939992`
  - retained metrics:
    - `ild_error = 4.256606211177914`
    - `itd_proxy_error = 0.01790328723936257`
    - `normalized_magnitude_error = 0.3462897991424333`
    - `nmse = 1.41251540184021`
  - acceptance: `paper_like_accept`
  - manifest check:
    - `solver_input_packed_shape = [513, 5, 15]`
    - `producer_session_id = SESSION-P2-0018`

Stage D decision:

- winner: `T09-I5-y0-s3401`
- reason:
  - `T09-I5-y0-s3401` and `T09-I6-y0-s3401` both reached `paper_like_accept`
  - `T09-I5-y0-s3401` kept the lower retained composite metric

## Stage E. Stability Check Across Seeds

- `T09-S1-y0-s3402`
  - retained composite: `5.941313809790523`
  - acceptance: `paper_like_accept`
- `T09-S2-y0-s3403`
  - retained composite: `5.925616885975415`
  - acceptance: `paper_like_accept`

Stage E decision:

- all three seeds:
  - `T09-I5-y0-s3401`
  - `T09-S1-y0-s3402`
  - `T09-S2-y0-s3403`
  remained at least `paper_like_accept`
- promotion result:
  - `promotion_granted_paper_like_stable`

## Stage F. Promoted Long Run

- promoted command family:
  - profile: `paper_ild_push_v1`
  - solver: `hidden_dim = 48`, `block_count = 3`, `rank = 8`
  - `alpha_init = 0.15`
  - `alpha_max = 0.35`
- executed run:
  - `T09-R2-y0-s3401`
- retained checkpoint result:
  - retained composite: `3.430381294454479`
  - best iteration: `7947`
  - final iteration: `8000`
  - stop reason: `max_iterations_reached`
  - retained metrics:
    - `ild_error = 1.7256287218571187`
    - `itd_proxy_error = 0.016510563573170753`
    - `normalized_magnitude_error = 0.30524950299696796`
    - `nmse = 1.3829925060272217`
  - acceptance:
    - `paper_like_accept`
    - not `four_down_accept`

Delta against the `EXP-0004` baseline:

- `ild_error`: `-10.994956552556832`
- `itd_proxy_error`: `-0.009696586826434708`
- `normalized_magnitude_error`: `-0.17351086343674699`
- `nmse`: `+0.012095808982849121`

Interpretation:

- the promoted long run improved three of the four baseline metrics dramatically
- `four_down_accept` still fails only because `nmse` remains slightly above baseline
- the run is still promotion-valid because the Stage D winner cleared `paper_like_accept` and passed the required two-seed stability check

## Session Decision

- This session does not end in `no_promotion`.
- Official decision:
  - `promotion_granted_paper_like_stable`
- Current promoted yaw `0` long-run authority:
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-R2-y0-s3401/`

## Continuation Recommendation

- Preserve the new screening and long-run artifacts:
  - `T09-P9-y0-s3401` through `T09-P13-y0-s3401`
  - `T09-I4-y0-s3401` through `T09-I6-y0-s3401`
  - `T09-S1-y0-s3402`
  - `T09-S2-y0-s3403`
  - `T09-R2-y0-s3401`
- Treat `T09-R2-y0-s3401` as the current best retained `TASK-0009` result.
- Do not reopen the old ILD mismatch or the old fake-energy-descriptor diagnosis; those remain closed.
- Next owner decision should focus on the promoted-result follow-up, not on rerun authorization:
  - decide whether the next experiment should try to recover the remaining NMSE gap on yaw `0`
  - decide whether the promoted `paper_ild_push_v1` / higher-capacity configuration should now be tested on yaw `90`
  - decide whether the energy-descriptor variant deserves a promoted long run of its own, given that `T09-I6-y0-s3401` also reached `paper_like_accept`
