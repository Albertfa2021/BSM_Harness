---
Document_ID: SESSION-P2-0007
Title: Residual Solver Loss Loop And Evaluation Export
Status: Stable
Phase: Phase_02_Development
Track: Session
Maturity: Consolidating
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 03_Sessions/Distillations/DIST-0007_TASK-0006_Closure_And_Phase02_Runnable_Loop.md
  - 04_Tasks/Completed/TASK-0005_Cue_Bank_And_Paper_Aligned_ITD_Core.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 01_Charter/Goals/20260324_BSM_Neural_Optimization_Plan.md
  - 03_Sessions/Distillations/DIST-0006_TASK-0005_Closure_And_TASK-0006_Handoff.md
Last_Updated: 2026-04-20
Review_Required: Yes
---

# Residual Solver Loss Loop And Evaluation Export

## Target Subtask

- Execute `TASK-0006` as the next Phase 02 implementation closure.
- Limit the session to:
  - solver input assembly
  - residual solver closure
  - first integrated loss loop
  - machine-readable evaluation export

## Reference Anchors

- `01_Charter/Goals/20260324_BSM_Neural_Optimization_Plan.md`
- `02_Architecture/Data/ARCH-04_Input_Output_Contracts.md`
- `02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md`
- `02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md`
- `04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md`

## Test Standard

### Scope

- The session changes only the solver input packer, residual solver, loss loop, and evaluation export boundary.

### Preconditions

- `conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank smoke` passes.
- Active environment must be `bsm_harness_py311`.
- The session must consume the project-side cue bank rather than re-implementing ILD or ITD helpers.

### Shape And Contract Checks

- Solver input pack must match the accepted tensor semantics from `ARCH-07` Step G.
- Residual output shape must match `c_magls`.
- Export summary must include baseline name, ILD error, ITD proxy error, normalized magnitude error, and NMSE.

### Numerical And Stability Checks

- Forward pass must remain finite.
- Backward pass must remain finite in the official `bsm_harness_py311` runtime.
- One short optimization run must reduce the total loss relative to initialization.

### Acceptance Checks

- One short-run experiment produces finite traces and machine-readable summary outputs.

## Completion Gate

- The session closes only after the predeclared short-run optimization/export command has been run and the result has been recorded here.

## Expected Deliverables

- One project-side solver input packer.
- One residual solver authority.
- One integrated loss loop using the shared renderer and cue bank.
- One machine-readable evaluation export path.

## Session Start State

- `TASK-0005` cue-bank smoke passed on `2026-04-17`.
- Cue-bank authority now exists through `bsm.phase02.cue_bank`.
- Environment follow-up inherited from `SESSION-P2-0006`:
  - the previous `torch` runtime issue in `bsm_harness_py311` was repaired on `2026-04-17`
  - `TASK-0005` now includes an official conda-gated backward-pass verification result
  - current working stack is the official `torch 2.5.1+cpu` pip wheel with restored `llvm-openmp` runtime

## 2026-04-20 Implementation Update

- Added `bsm.phase02.residual_solver` as the TASK-0006 project-side authority for:
  - solver input packing from `c_ls`, `c_magls`, `c_magls - c_ls`, normalized frequency index, and normalized coefficient index
  - `FCR-Mixer` residual solver outputting `delta_c[f, m, e]` plus explicit bounded `alpha`
  - coefficient composition through `c_joint = c_magls + alpha * delta_c`
  - shared torch renderer path using the same `V[d, f, m]` semantics as the baseline renderer
  - integrated loss loop with magnitude, magnitude-derivative, ILD proxy, GCC-PHAT ITD proxy, and residual regularization terms
  - machine-readable `summary.json` and `loss_trace.jsonl` export
- Added `compute_ild_loss_torch` to `bsm.phase02.cue_bank` as an autograd-ready broadband ILD optimization proxy.
- Preserved the existing ERB-band auditory ILD path for exported evaluation metrics through `build_cue_bank`.
- Added regression coverage in:
  - `bsm.tests.test_cue_bank`
  - `bsm.tests.test_residual_solver`

## Short-Run Gate Result

- Command:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

- Result:
  - `ok = true`
  - `initial_loss_total = 1.6027357578277588`
  - `final_loss_total = 1.5498015880584717`
  - `selected_iteration = 1`
  - `normalized_magnitude_error = 0.12459041371202112`
  - `nmse = 0.28486496210098267`
  - `ild_error = 5.2882367741325496`
  - `itd_proxy_error = 0.004026206304279611`
- Export artifacts:
  - `06_Assets/Generated_Artifacts/TASK-0006/20260420T034925Z/summary.json`
  - `06_Assets/Generated_Artifacts/TASK-0006/20260420T034925Z/loss_trace.jsonl`

## Regression Verification

- TASK-0006 focused tests:

```bash
conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_cue_bank bsm.tests.test_residual_solver
```

- Full discovered project-side test suite:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

- Result:
  - `20` tests passed in the official `bsm_harness_py311` environment.
