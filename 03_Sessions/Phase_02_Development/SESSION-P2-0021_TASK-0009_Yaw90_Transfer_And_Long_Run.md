---
Document_ID: SESSION-P2-0021
Title: TASK-0009 Yaw90 Transfer And Long Run
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
  - 05_Experiments/EXP-0003_TASK-0009_Planned_Optimization_Campaign/README.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0020_TASK-0009_Post_Promotion_Yaw0_NMSE_Followup_Execution.md
  - 05_Experiments/Registry/Result_Tracker.md
  - 06_Assets/Generated_Artifacts/Index.md
Last_Updated: 2026-04-23
Review_Required: Yes
---

# TASK-0009 Yaw90 Transfer And Long Run

## Target Subtask

- Continue from `SESSION-P2-0020` after the narrow yaw `0` NMSE gap-closure batch failed to justify another yaw `0` long run.
- Follow the documented fallback priority:
  - transfer the promoted non-energy-descriptor configuration to yaw `90`
- Keep the promoted configuration fixed as the transfer source:
  - `paper_ild_push_v1`
  - `hidden_dim = 48`
  - `block_count = 3`
  - `rank = 8`
  - `alpha_init = 0.15`
  - `alpha_max = 0.35`
  - full `513` bins
  - unified paper-aligned ILD metric
- Use a minimal yaw `90` comparison batch first and authorize a long run only if the transfer batch is clearly good enough.

## Runtime Closure

- Regression gate:
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests`
  - result:
    - `39` tests passed
- Updated `bsm.phase02.task09_runner` so this session records:
  - `producer_session_id = SESSION-P2-0021`

## yaw `90` Baseline Authority

- yaw `90` baseline from the embedded comparison authority in `T09-P2-y90-s3401`:
  - `ild_error = 14.648233602428062`
  - `itd_proxy_error = 0.025814691019366023`
  - `normalized_magnitude_error = 0.5019428959076118`
  - `nmse = 1.5557793378829956`
- historical retained yaw `90` authority before this session:
  - `T09-P2-y90-s3401`
  - retained metrics:
    - `ild_error = 12.426451951934242`
    - `itd_proxy_error = 0.025146023654862442`
    - `normalized_magnitude_error = 0.43193991205883736`
    - `nmse = 1.5427275896072388`

## Narrow yaw `90` Transfer Batch

- Batch artifact:
  - `06_Assets/Generated_Artifacts/TASK-0009/yaw90_transfer_followup_SESSION-P2-0021_y90_s3401/comparison_summary.json`

### Run Matrix

- `T09-Y1-y90-s3401`
  - exact promoted transfer
  - `paper_ild_push_v1`
- `T09-Y2-y90-s3401`
  - companion transfer with light late `dmag` protection
  - `paper_ild_push_v1_late_dmag_guard`

### Retained Results

- `T09-Y1-y90-s3401`
  - retained composite: `5.545048044127539`
  - retained metrics:
    - `ild_error = 3.6784228873248677`
    - `itd_proxy_error = 0.012569386669750592`
    - `normalized_magnitude_error = 0.3828190643528923`
    - `nmse = 1.4712367057800293`
  - verdict against yaw `90` baseline:
    - `four_down_accept`
- `T09-Y2-y90-s3401`
  - retained composite: `5.759343232454394`
  - retained metrics:
    - `ild_error = 3.8806645554384005`
    - `itd_proxy_error = 0.012969140186342322`
    - `normalized_magnitude_error = 0.3803993399531249`
    - `nmse = 1.4853101968765259`
  - verdict against yaw `90` baseline:
    - `four_down_accept`

### Narrow-Batch Decision

- winner:
  - `T09-Y1-y90-s3401`
- reason:
  - lower retained composite than `T09-Y2-y90-s3401`
  - still satisfies strict four-metric baseline improvement
- promotion decision:
  - `promotion_granted_yaw90_long_run`

## Promoted yaw `90` Long Run

- executed run:
  - `T09-R1-y90-s3401`
- retained composite:
  - `3.004526558601078`
- best iteration:
  - `7912`
- retained metrics:
  - `ild_error = 1.2432368569310537`
  - `itd_proxy_error = 0.010711959455913524`
  - `normalized_magnitude_error = 0.6434078756522211`
  - `nmse = 1.1071698665618896`

## Interpretation

- `T09-R1-y90-s3401` is the strongest yaw `90` retained checkpoint on runner composite, ILD, ITD, and NMSE.
- `T09-R1-y90-s3401` is not a strict yaw `90` four-down retained run because:
  - `normalized_magnitude_error = 0.6434078756522211`
  - baseline `normalized_magnitude_error = 0.5019428959076118`
- therefore this session keeps two useful yaw `90` authority views:
  - conservative four-down retained checkpoint:
    - `T09-Y1-y90-s3401`
  - promoted long-run composite authority:
    - `T09-R1-y90-s3401`

## Session Decision

- official result:
  - `promotion_granted_yaw90_long_run_executed`
- retained authority statement:
  - yaw `90` transfer is now proven
  - `T09-Y1-y90-s3401` is the best strict four-down yaw `90` retained checkpoint
  - `T09-R1-y90-s3401` is the best composite yaw `90` long-run retained checkpoint

## Continuation Recommendation

- Preserve the new yaw `90` artifacts:
  - `T09-Y1-y90-s3401`
  - `T09-Y2-y90-s3401`
  - `T09-R1-y90-s3401`
  - `yaw90_transfer_followup_SESSION-P2-0021_y90_s3401/comparison_summary.json`
- Do not rerun the exact same non-energy yaw `90` transfer batch immediately.
- The next follow-up question can now move to:
  - whether the repaired energy-descriptor route deserves a yaw `90` comparison batch of its own
  - or whether documentation should nominate `T09-Y1-y90-s3401` versus `T09-R1-y90-s3401` as the primary yaw `90` authority depending on whether strict four-down or retained composite is the decision rule
