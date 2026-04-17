---
Document_ID: ARCH-05
Title: Risk Register
Status: Draft
Phase: Phase_02_Development
Track: Architecture
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Distillations/DIST-0002_Phase01_Architecture_Baseline.md
  - 01_Charter/Goals/CHAR-06_Phase_01_Execution_Plan.md
  - 01_Charter/Assumptions/CHAR-05_Core_Assumptions.md
  - 06_Assets/External_Dependencies/Index.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Risk Register

## R1. Dependency And Asset Drift

- Risk:
  - external files, Git-based dependencies, or mirrored baseline assets may become unavailable or diverge from the documented setup
- Impact:
  - front-end reproduction becomes non-repeatable
- Mitigation:
  - keep dependency records in `06_Assets/External_Dependencies/`
  - register missing or downloaded assets explicitly before using them in experiments

## R2. Reference Tree Contamination

- Risk:
  - implementation work leaks into `07_References/`, breaking the separation between project code and imported baselines
- Impact:
  - traceability and future upstream comparison become harder
- Mitigation:
  - keep imported trees read-only
  - place new implementation in project work areas such as `05_Experiments/`

## R3. Premature Interface Refactor

- Risk:
  - restructuring modules before the front-end semantics are stabilized may destroy useful baseline context
- Impact:
  - lost comparability against `Array2Binaural` and slower convergence on the actual solver loop
- Mitigation:
  - freeze semantic contracts first
  - allow code layout to stay flexible until more experiments exist

## R4. Objective Conflict

- Risk:
  - magnitude, ILD, ITD, and regularization terms may push the solver in incompatible directions
- Impact:
  - unstable optimization or improvement in one cue at the cost of another
- Mitigation:
  - keep per-loss logging mandatory
  - compare against `BSM-MagLS`
  - use ablations on weights and `alpha`

## R5. Cue Mismatch Between Training And Evaluation

- Risk:
  - the ILD or ITD paths used inside optimization may drift from the evaluation definitions
- Impact:
  - reported metric gains become hard to interpret
- Mitigation:
  - use the same semantic cue modules for loss and evaluation whenever possible
  - document any proxy-versus-metric gap explicitly

## R6. Scope Creep Into Dynamic Head Tracking

- Risk:
  - the project starts mixing static Phase 01 work with dynamic yaw trajectory requirements too early
- Impact:
  - architecture complexity increases before a static baseline is closed
- Mitigation:
  - keep static head orientation as the fixed Phase 01 scope
  - treat dynamic yaw as a reserved extension point only
