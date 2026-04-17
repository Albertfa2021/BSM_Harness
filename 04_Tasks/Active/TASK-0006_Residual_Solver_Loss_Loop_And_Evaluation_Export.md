---
Document_ID: TASK-0006
Title: Residual Solver Loss Loop And Evaluation Export
Status: Active
Phase: Phase_02_Development
Track: Task
Maturity: Planned
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 01_Charter/Goals/20260324_BSM_Neural_Optimization_Plan.md
  - 01_Charter/Goals/CHAR-07_Phase_02_Detailed_Plan.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
Last_Updated: 2026-04-17
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

## Session Policy

- Exactly one development session should be allocated to this subtask before moving on.
- If the scope grows beyond one verified loop closure, split out a new task rather than broadening this one silently.

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

## Completion Evidence

- One session note with short-run optimization trace summary.
- One export artifact path recorded in the session note and task outcome.
