---
Document_ID: DIST-0006
Title: TASK-0005 Closure And TASK-0006 Handoff
Status: Draft
Phase: Phase_02_Development
Track: Session
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Phase_02_Development/SESSION-P2-0006_Cue_Bank_And_Paper_Aligned_ITD_Core.md
  - 04_Tasks/Completed/TASK-0005_Cue_Bank_And_Paper_Aligned_ITD_Core.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0007_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 00_Governance/Manifest/MANI-00_Project_State.md
  - 00_Governance/Manifest/MANI-02_Active_Focus.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# TASK-0005 Closure And TASK-0006 Handoff

## Distilled Consensus

- `TASK-0005` is now closed at the cue-bank and paper-aligned ITD core boundary.
- The closure evidence is:
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_baseline_renderer bsm.tests.test_cue_bank`
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_cue_bank.CueBankTests.test_torch_itd_loss_supports_finite_backward_pass`
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank smoke`
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank report --baseline-name BSM-MagLS`
- The project-side cue authority now exists through:
  - `bsm.phase02.cue_bank`
- The cue bank now emits the expected public cue objects:
  - `erb_center_freq_hz[b]`
  - `ild_ref[b, d]`
  - `ild_est[b, d]`
  - `gcc_phat_ref[d, t]`
  - `gcc_phat_est[d, t]`
- The accepted default ITD configuration recorded at closure is:
  - `sample_rate_hz = 32000`
  - `tau = 0.001 s`
  - `tau_samples = 32`
  - low-frequency gating disabled
- The optimization-readiness acceptance item that had been environment-limited is now also closed:
  - the differentiable ITD helper completes a finite backward pass inside `bsm_harness_py311`
- The next active implementation boundary is `TASK-0006`, with a fresh development session note opened before coding.

## Commit Targets

- `bsm/phase02/`
- `bsm/tests/`
- `03_Sessions/`
- `04_Tasks/`
- `00_Governance/Manifest/`

## Scope Guard

- Do not bypass the shared cue bank when implementing `TASK-0006`.
- Treat the repaired conda-level `torch` issue as a closed environment maintenance follow-up, not as an open cue-bank blocker.
- Do not advance beyond the first short-run optimization/export closure before opening a new task.
