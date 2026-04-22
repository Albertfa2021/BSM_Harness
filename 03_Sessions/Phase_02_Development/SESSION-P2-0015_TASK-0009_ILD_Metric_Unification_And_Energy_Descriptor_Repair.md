---
Document_ID: SESSION-P2-0015
Title: TASK-0009 ILD Metric Unification And Energy Descriptor Repair
Status: Stable
Phase: Phase_02_Development
Track: Session
Maturity: Execution
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0014_TASK-0009_Baseline_Not_Beaten_Diagnosis_And_Repair_Plan.md
Last_Updated: 2026-04-22
Review_Required: Yes
---

# TASK-0009 ILD Metric Unification And Energy Descriptor Repair

## Target Subtask

- Unify the `TASK-0009` ILD training/evaluation path around one paper-aligned frequency-band definition.
- Repair the `include_front_end_energy_descriptor` plumbing so the ablation becomes real.

## Runtime Closure

- Updated `bsm.phase02.cue_bank`:
  - ILD defaults now follow the cited paper direction more closely:
    - `23` bands
    - lower bound `1.5 kHz`
    - upper bound requested as `20 kHz`, clipped by repository Nyquist
  - `build_cue_bank(...)` now computes ILD from paper-aligned banded frequency integration rather than the previous broad auditory proxy path
  - `compute_ild_loss_torch(...)` now uses the same banded ILD definition as evaluation
  - training-side ILD loss and exported ILD metric are now based on the same per-band ILD object
- Updated `bsm.phase02.residual_solver`:
  - `compute_loss_breakdown_torch(...)` now passes `sample_rate_hz` into the unified ILD loss path
- Updated `bsm.phase02.task09_runner`:
  - `_build_solver_assets(...)` now passes `include_front_end_energy_descriptor` into `build_solver_input_pack(...)`
  - `run_manifest.json` now records `solver_input_summary`
  - energy-descriptor runs now expose the extra solver-input channel in artifacts

## Verification

- Targeted regression:

```bash
conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_cue_bank bsm.tests.test_residual_solver bsm.tests.test_task09_runner
```

- Result:
  - `20` tests passed

- Full regression:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

- Result:
  - `39` tests passed

- Real-path smoke checks:
  - full-`513` short `TASK-0009` run passed and exported finite comparison metrics
  - energy-descriptor short `TASK-0009` run passed and exported `solver_input_packed_shape = [33, 5, 15]`

## Immediate Follow-up

- The metric family is now unified enough to make the next `TASK-0009` rerun meaningful.
- The next blocker question is no longer whether the energy-descriptor variant was fake.
- The next real question is whether the paper-aligned banded ILD objective can beat the baseline under a longer authoritative run.
