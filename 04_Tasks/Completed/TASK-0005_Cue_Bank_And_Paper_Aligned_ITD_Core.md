---
Document_ID: TASK-0005
Title: Cue Bank And Paper Aligned ITD Core
Status: Stable
Phase: Phase_02_Development
Track: Task
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Phase_02_Development/SESSION-P2-0006_Cue_Bank_And_Paper_Aligned_ITD_Core.md
  - 03_Sessions/Distillations/DIST-0006_TASK-0005_Closure_And_TASK-0006_Handoff.md
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 01_Charter/Goals/CHAR-07_Phase_02_Detailed_Plan.md
  - 02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 05_Experiments/EXP-0001_Auditory_ILD_Python/README.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Cue Bank And Paper Aligned ITD Core

## Scope

- Integrate the existing auditory ILD path into the formal cue module.
- Implement the first differentiable ITD path using the ITD-loss paper definition.

## Reference Or Authority

- Direct anchors:
  - `EXP-0001_Auditory_ILD_Python/code/auditory_ild.py`
  - `Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf`
- Contract authority:
  - `ARCH-04` Contract 7
  - `ARCH-07` Step F and Step F1

## Session Policy

- Exactly one development session should be allocated to this subtask before moving on.
- That session must not add residual solver code.

## Predeclared Test Standard

- Type:
  - Reference parity plus optimization readiness
- Preconditions:
  - `TASK-0004` smoke path passes
  - `conda activate bsm_harness_py311`
- Required checks:
  - ILD helper outputs match current auditory replication expectations
  - ITD helper computes GCC-PHAT cross-correlation sequences inside `[-tau, tau]`
  - ITD loss returns finite values
  - if implemented in differentiable code, backward pass is finite
- Completion gate:
  - one smoke path runs ILD and ITD helpers on simple binaural examples and passes

## Completion Evidence

- One session note with ILD and ITD smoke outputs.
- Explicit record of `tau`, sample rate, and any low-frequency gating choices.

## Outcome

- Added `bsm.phase02.cue_bank` as the project-side cue authority for:
  - ERB-band ILD outputs using the existing `auditory_ild.py` reference implementation
  - GCC-PHAT cross-correlation windows inside the configured `[-tau, tau]` lag range
  - paper-aligned sequence-MSE `itd_proxy_error`
- Added project-side CLI entry points for:
  - `report`
  - `smoke`
- Added project-side cue-bank coverage in `bsm.tests.test_cue_bank`.
- Verified closure with:
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_baseline_renderer bsm.tests.test_cue_bank`
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_cue_bank.CueBankTests.test_torch_itd_loss_supports_finite_backward_pass`
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank smoke`
  - `conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank report --baseline-name BSM-MagLS`
- Recorded configuration choices:
  - `sample_rate_hz = 32000`
  - `tau = 0.001 s`
  - `tau_samples = 32`
  - low-frequency gating disabled by default
- Optimization-readiness closure note:
  - the differentiable ITD path now completes its backward-pass check inside the official `bsm_harness_py311` conda environment
  - no `TASK-0005` acceptance item remains open due to the earlier torch runtime failure
