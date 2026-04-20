---
Document_ID: TASK-0006
Title: Residual Solver Loss Loop And Evaluation Export
Status: Stable
Phase: Phase_02_Development
Track: Task
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Phase_02_Development/SESSION-P2-0007_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md
  - 03_Sessions/Distillations/DIST-0006_TASK-0005_Closure_And_TASK-0006_Handoff.md
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 01_Charter/Goals/20260324_BSM_Neural_Optimization_Plan.md
  - 01_Charter/Goals/CHAR-07_Phase_02_Detailed_Plan.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
Last_Updated: 2026-04-20
Review_Required: Yes
---

# Residual Solver Loss Loop And Evaluation Export

## Scope

- Build the project-side solver input packer, residual solver, loss loop, and evaluation export path.
- Close the first full joint optimization loop against `BSM-MagLS`.

## Reference Or Authority

- No direct external solver anchor exists.
- Design authority:
  - `20260324_BSM_Neural_Optimization_Plan.md` Section 四 to Section 七
  - `ARCH-04` Contract 4, Contract 5, and Contract 8
  - `ARCH-07` Step G to Step J

## Predeclared Test Standard

- Type:
  - Contract conformance plus optimization readiness
- Preconditions:
  - `TASK-0005` smoke path passes
  - `conda activate bsm_harness_py311`
- Required checks:
  - solver input pack matches declared tensor semantics
  - forward pass is finite
  - backward pass is finite
  - one short optimization run reduces total loss relative to initialization
  - export contains baseline name, ILD error, ITD proxy error, normalized magnitude error, and NMSE
- Completion gate:
  - one short-run experiment produces finite traces and machine-readable summary outputs

## Outcome

- Added `bsm.phase02.residual_solver` as the project-side authority for:
  - solver input packing
  - `FCR-Mixer` residual prediction
  - explicit bounded `alpha`
  - joint coefficient composition
  - torch shared rendering
  - integrated loss breakdown
  - machine-readable summary and trace export
- Added `bsm.phase02.cue_bank.compute_ild_loss_torch` for the autograd loss loop.
- Added regression coverage in `bsm.tests.test_residual_solver`.
- Preserved exported ERB-band ILD evaluation through `bsm.phase02.cue_bank.build_cue_bank`.

## Completion Evidence

- TASK-0006 short-run export gate:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

- Gate result:
  - `ok = true`
  - `initial_loss_total = 1.6027357578277588`
  - `final_loss_total = 1.5498015880584717`
  - `selected_iteration = 1`
- Export artifacts:
  - `06_Assets/Generated_Artifacts/TASK-0006/20260420T034925Z/summary.json`
  - `06_Assets/Generated_Artifacts/TASK-0006/20260420T034925Z/loss_trace.jsonl`
- Regression:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

- Regression result:
  - `20` tests passed.
