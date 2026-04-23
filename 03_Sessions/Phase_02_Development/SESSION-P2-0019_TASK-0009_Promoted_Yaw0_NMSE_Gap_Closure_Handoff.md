---
Document_ID: SESSION-P2-0019
Title: TASK-0009 Promoted Yaw0 NMSE Gap Closure Handoff
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
  - 03_Sessions/Phase_02_Development/SESSION-P2-0018_TASK-0009_Official_Full513_Rerun_And_Promotion.md
Last_Updated: 2026-04-23
Review_Required: Yes
---

# TASK-0009 Promoted Yaw0 NMSE Gap Closure Handoff

## Target Subtask

- Carry forward the promoted `TASK-0009` yaw `0` result from `SESSION-P2-0018`.
- Do not spend the next session re-proving that promotion is allowed.
- Make the next session a narrow `yaw 0` follow-up that targets the remaining `nmse` gap while preserving the strong ILD / ITD / magnitude gains already achieved.

## Why This Is The First Follow-up

- `T09-R2-y0-s3401` already reached stable `paper_like_accept`.
- It still misses `four_down_accept` for only one reason:
  - `nmse = 1.3829925060272217`
  - baseline `nmse = 1.3708966970443726`
- Therefore the cheapest next question is:
  - can a narrow follow-up on the promoted `yaw 0` route close the remaining `nmse` gap without giving back the large ILD / ITD / magnitude improvements

## Locked Carry-Forward Authority

Treat the following as fixed unless the next session finds explicit contradictory evidence:

- retained promoted artifact:
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-R2-y0-s3401/`
- batch summary authority:
  - `06_Assets/Generated_Artifacts/TASK-0009/official_full513_rerun_SESSION-P2-0018_y0_s3401_summary.json`
- promoted loss profile:
  - `paper_ild_push_v1`
- promoted solver shape:
  - `hidden_dim = 48`
  - `block_count = 3`
  - `rank = 8`
  - `alpha_init = 0.15`
  - `alpha_max = 0.35`
- optimization / comparison authority:
  - full `513` bins
  - unified paper-aligned ILD metric
  - `EXP-0004` baseline thresholds

## Explicit Priority Decision

The next session should not start from yaw `90`.

The next session should not start from a broad hyperparameter sweep.

The next session should start from one narrow priority:

- `yaw 0` promoted-route `nmse` gap closure

Fallback priorities only if the chosen narrow `yaw 0` follow-up clearly fails:

- second priority:
  - transfer the promoted non-energy-descriptor configuration to yaw `90`
- third priority:
  - test whether the repaired energy-descriptor route deserves its own promoted long run

## Narrow Search Policy

Keep the next session small and deliberate.

Recommended candidate count:

- `2` to `3` variants total

Recommended variant style:

- keep the promoted solver shape fixed
- keep `paper_ild_push_v1` as the starting point
- introduce only light magnitude / `nmse` protection adjustments

Good examples:

- a slightly less ILD-aggressive schedule that restores a bit more `mag` / `dmag` pressure late in training
- a near-promoted profile that keeps Stage D capacity but softens the final-stage ILD push
- a retained-checkpoint policy check only if the next session can justify it narrowly from traces rather than by broad search

Avoid:

- reopening old metric-definition questions
- reopening old energy-descriptor plumbing questions
- switching orientation immediately
- launching more than one new long run before the narrow comparison is reviewed

## Acceptance Rule For The Next Session

Primary target:

- `four_down_accept`

That means all four retained metrics must improve against the `EXP-0004` baseline:

- `ild_error < 12.72058527441395`
- `itd_proxy_error < 0.02620715039960546`
- `normalized_magnitude_error < 0.47876036643371495`
- `nmse < 1.3708966970443726`

Interpretation rule:

- do not downgrade the promoted route if a narrow follow-up fails
- compare new narrow variants against:
  - the written `EXP-0004` baseline
  - the current promoted authority `T09-R2-y0-s3401`

## Suggested Next-Session Execution Order

1. Read:
   - `MANI-03`
   - `SESSION-P2-0018`
   - this handoff note
   - `TASK-0009`
   - `EXP-0004`
2. Re-run regression gate before new execution:
   - `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests`
3. Define `2` to `3` narrow `yaw 0` variants around the promoted route.
4. Run only the narrow comparison batch first.
5. Grant any new long run only if one narrow retained run clearly improves on `T09-R2-y0-s3401` in the intended direction and ideally reaches `four_down_accept`.

## Documentation Rule

This handoff session is documentation-only.

- no new runtime execution was performed here
- no new artifact directories were produced here

The next execution session should record:

- the chosen narrow run matrix
- why each variant is intended to help `nmse`
- whether any variant justifies another promoted long run
