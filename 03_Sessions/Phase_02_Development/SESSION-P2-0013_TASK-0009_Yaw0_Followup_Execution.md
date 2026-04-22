---
Document_ID: SESSION-P2-0013
Title: TASK-0009 yaw 0 Follow-up Execution
Status: Stable
Phase: Phase_02_Development
Track: Session
Maturity: Execution
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0012_TASK-0009_Yaw0_Followup_Planning.md
  - 05_Experiments/Registry/Result_Tracker.md
  - 06_Assets/Generated_Artifacts/Index.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
Last_Updated: 2026-04-22
Review_Required: Yes
---

# TASK-0009 yaw 0 Follow-up Execution

## Target Subtask

- Execute the written `EXP-0004` yaw `0` follow-up screening without redesigning the accepted `TASK-0008` route.
- Add the missing paper-inspired loss profiles required by the follow-up plan.
- Record one explicit retained-result decision before any seed-stability rerun or promoted long run is allowed.

## Runtime Closure

- Added the required `EXP-0004` loss profiles to `bsm.phase02.task09_runner`:
  - `paper_ild_guarded_v1`
  - `paper_ild_push_v1`
  - `paper_ild_push_v2`
- Added a direct registration test for those profiles in `bsm.tests.test_task09_runner`.
- Regression gate before edits:
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests`
  - `34` tests passed
- Regression gate after edits:
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests`
  - `35` tests passed

## Smoke Result

- `T09-SM1-y0-s3401`
  - profile: `paper_ild_guarded_v1`
  - retained composite: `13.87167153022196`
  - retained metrics:
    - `ild_error = 12.007554899760194`
    - `itd_proxy_error = 0.02614475910905723`
    - `normalized_magnitude_error = 0.46341985986284057`
    - `nmse = 1.3745520114898682`
  - retained verdict: `baseline_not_beaten`
  - smoke acceptance outcome:
    - no crash
    - finite exported metrics
    - `comparison_summary.json` present
    - checkpoint writes present
  - artifact root: `06_Assets/Generated_Artifacts/TASK-0009/T09-SM1-y0-s3401/`

## Stage C. Official Loss-Policy Screening

- `T09-P4-y0-s3401`
  - profile: `balanced_norm_v1`
  - retained composite: `15.37894172009149`
  - retained metrics:
    - `ild_error = 13.51313102121139`
    - `itd_proxy_error = 0.026071663077913834`
    - `normalized_magnitude_error = 0.4501728527119768`
    - `nmse = 1.38956618309021`
  - verdict: `baseline_not_beaten`
- `T09-P5-y0-s3401`
  - profile: `spatial_norm_v1`
  - retained composite: `15.932774359635284`
  - retained metrics:
    - `ild_error = 14.080853928648756`
    - `itd_proxy_error = 0.025972954905552348`
    - `normalized_magnitude_error = 0.46372385089787`
    - `nmse = 1.3622236251831055`
  - verdict: `baseline_not_beaten`
- `T09-P6-y0-s3401`
  - profile: `paper_ild_guarded_v1`
  - retained composite: `15.603606969640134`
  - retained metrics:
    - `ild_error = 13.74602203508806`
    - `itd_proxy_error = 0.026059564039591424`
    - `normalized_magnitude_error = 0.4572735280137025`
    - `nmse = 1.3742518424987793`
  - verdict: `baseline_not_beaten`
- `T09-P7-y0-s3401`
  - profile: `paper_ild_push_v1`
  - retained composite: `15.940146204930313`
  - retained metrics:
    - `ild_error = 14.094582004118234`
    - `itd_proxy_error = 0.02599874040081318`
    - `normalized_magnitude_error = 0.4741163704072984`
    - `nmse = 1.3454490900039673`
  - verdict: `baseline_not_beaten`
- `T09-P8-y0-s3401`
  - profile: `paper_ild_push_v2`
  - retained composite: `15.926695200953928`
  - retained metrics:
    - `ild_error = 14.081682593689775`
    - `itd_proxy_error = 0.026049321530272042`
    - `normalized_magnitude_error = 0.4716263974205878`
    - `nmse = 1.3473368883132935`
  - verdict: `baseline_not_beaten`

## Stage D. Narrow Initialization / Capacity Screening

- Best Stage C profile by retained composite remained `balanced_norm_v1`, so Stage D used that profile for all three variants.
- `T09-I1-y0-s3401`
  - solver variant: conservative `alpha_init = 0.05`, `alpha_max = 0.20`
  - retained composite: `15.527648652411148`
  - verdict: `baseline_not_beaten`
- `T09-I2-y0-s3401`
  - solver variant: higher capacity with `hidden_dim = 48`, `block_count = 3`, `rank = 8`
  - retained composite: `15.417732386776184`
  - verdict: `baseline_not_beaten`
- `T09-I3-y0-s3401`
  - solver variant: same higher-capacity setting plus `include_front_end_energy_descriptor = true`
  - retained composite: `15.417732386776184`
  - verdict: `baseline_not_beaten`

## Acceptance Result

- No retained run reached `four_down_accept`.
- No retained run reached `paper_like_accept`.
- Therefore:
  - `Stage E` seed-stability reruns were not launched
  - `Stage F` promoted long-run execution was not launched
- Session decision: `no_promotion`

## Baseline Audit Result

- The written `EXP-0004` yaw `0` baseline to beat was:
  - `ild_error = 9.526687421752532`
  - `itd_proxy_error = 0.02620715039960546`
  - `normalized_magnitude_error = 0.47876036643371495`
  - `nmse = 1.3708966970443726`
- The current runner-exported baseline in this session's `comparison_summary.json` files was:
  - `ild_error = 7.566111586868448`
  - `itd_proxy_error = 0.01798799263605173`
  - `normalized_magnitude_error = 0.34135829556077496`
  - `nmse = 1.4027093648910522`
- The mismatch is explained by comparison resolution, not by an unexplained baseline mutation:
  - the written `EXP-0004` values match the current code when yaw `0` baseline metrics are computed on the full `513`-bin front-end bundle
  - the runner-exported values match the current code when the same yaw `0` baseline metrics are recomputed on the pilot run's sliced `129`-bin bundle
- Therefore the follow-up session mixed two comparison authorities:
  - written acceptance thresholds from full-frequency validation artifacts
  - exported `comparison_summary.json` baselines from reduced-frequency screening artifacts

## Authority Repair

- Owner decision:
  - use full-frequency `513` as the comparison authority
- Implemented repair:
  - `bsm.phase02.task09_runner` now evaluates retained checkpoints and declared baselines on the full selected-orientation bundle even when training ran on a sliced pilot bundle
  - learned pilot coefficients are expanded back into the full-frequency coefficient tensor before retained-response rendering
- Verification:
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_task09_runner`
  - `6` tests passed
  - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests`
  - `36` tests passed
- Artifact refresh:
  - existing `TASK-0009` `comparison_summary.json` files were rewritten with the repaired full-`513` authority
  - yaw `0` runs now export the baseline declared in `EXP-0004`
  - yaw `90` runs now also export full-frequency baseline comparisons rather than sliced pilot-only baselines
  - refreshed `yaw 0` ranking still keeps `T09-P4-y0-s3401` as the best Stage C retained run, while `T09-I2-y0-s3401` and `T09-I3-y0-s3401` now tie as the best Stage D retained runs

## Continuation Recommendation

- Preserve all yaw `0` follow-up artifacts under `06_Assets/Generated_Artifacts/TASK-0009/`.
- Keep the explicit `no_promotion` decision in force.
- Do not launch seed-stability reruns or a promoted long run from the current evidence.
- Use the repaired full-`513` comparison authority for the next `TASK-0009` decision.
- Then decide whether to:
  - rerun yaw `0`
  - revisit yaw `90`
  - open a blocker on baseline authority / comparison semantics
