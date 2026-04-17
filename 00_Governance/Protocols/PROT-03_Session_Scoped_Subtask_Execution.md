---
Document_ID: PROT-03
Title: Session Scoped Subtask Execution
Status: Draft
Phase: Phase_02_Development
Track: Governance
Maturity: Consolidating
Related_Docs:
  - 00_Governance/Protocols/PROT-02_Workflow_Capture_Align_Commit.md
  - 03_Sessions/Phase_02_Development/Index.md
  - 04_Tasks/Active/Index.md
  - 01_Charter/Goals/CHAR-07_Phase_02_Detailed_Plan.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Session Scoped Subtask Execution

## Rule

- During active implementation, one development session handles exactly one subtask.
- A subtask is not allowed to start coding before its test standard has been written down.
- A session is only considered complete after the predeclared tests have been run and the results have been recorded.

## Required Session Order

1. Select one active task from `04_Tasks/Active/`.
2. Open or create one session note in `03_Sessions/Phase_02_Development/`.
3. Write the session header sections before implementation:
   - target subtask
   - reference anchors or plan authority
   - test standard
   - completion gate
4. Implement only that subtask.
5. Run the predeclared tests.
6. Record pass/fail results and open issues in the same session note.
7. If the subtask is complete, move or rewrite the task record accordingly and update formal documents if needed.

## What A Test Standard Must Contain

- Scope:
  - what exact module or contract is being changed
- Preconditions:
  - required conda environment
  - required assets or generated files
- Shape checks:
  - mandatory tensor or interface checks
- Numerical checks:
  - `nan/inf` rejection
  - stability or parity checks where applicable
- Acceptance checks:
  - the minimal successful behavior that must hold before the session can close

## Variable And Interface Discipline

- A session must name public variables and outputs using the canonical schema terms from `ARCH-03`.
- If the session introduces a new reusable artifact, the session note must record:
  - canonical object name
  - producer task and session
  - version metadata location
  - contract it satisfies in `ARCH-04`
- If the implementation uses internal packed names or temporary aliases, the session note must map them back to the canonical public names before closing.

## Allowed Test Standard Types

### Type A. Reference Parity

- Use when the subtask wraps or reproduces a direct external anchor.
- Example:
  - ILD replication against Matlab-derived behavior
  - front-end or baseline reconstruction against imported baseline semantics

### Type B. Contract Conformance

- Use when the subtask has no direct external implementation anchor.
- The authority is then:
  - `ARCH-03`
  - `ARCH-04`
  - `ARCH-06`
  - `ARCH-07`
  - `20260324_BSM_Neural_Optimization_Plan.md`

### Type C. Optimization Readiness

- Use when the subtask is meant to be consumed by gradient-based optimization.
- Must include:
  - forward pass finiteness
  - backward pass finiteness
  - one short-run loss decrease check if the module is already integrated into a loop

## Session Close Conditions

- A session cannot close as `done` if its planned tests were skipped.
- A session may close as `partial` only if:
  - the failed or missing tests are explicitly recorded
  - the next blocking condition is written down
  - the linked task remains active or moves to blocked

## Task And Session Relationship

- Each active task file must define:
  - subtask scope
  - reference anchors or plan authority
  - required test standard
  - completion evidence
- Each development session note must point to exactly one active task file.
- If the work expands beyond one subtask, open a new task and a new session rather than silently broadening scope.

## Phase 02 Operating Rule

- Phase 02 proceeds by a chain of small verified closures, not by one large implementation burst.
- The accepted sequence is:
  - asset resolver
  - direction grids and front-end bundle
  - baseline coefficient builder and renderer
  - cue bank and ITD paper path
  - solver input assembly and residual solver
  - loss loop and evaluation export
