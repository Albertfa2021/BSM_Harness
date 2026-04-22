---
Document_ID: SESSION-P2-0014
Title: TASK-0009 Baseline Not Beaten Diagnosis And Repair Plan
Status: Stable
Phase: Phase_02_Development
Track: Session
Maturity: Planning
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0013_TASK-0009_Yaw0_Followup_Execution.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
Last_Updated: 2026-04-22
Review_Required: Yes
---

# TASK-0009 Baseline Not Beaten Diagnosis And Repair Plan

## Target Subtask

- Diagnose why the repaired full-`513` comparison authority still reports `baseline_not_beaten`.
- Repair confirmed optimization-module faults before any new `TASK-0009` screening run is treated as authoritative.
- Write a narrow next-session protocol that can either justify one repaired rerun or open a blocker cleanly.

## Reference Anchors

- Task authority:
  - `04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md`
- Current experiment authority:
  - `05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md`
- Latest execution evidence:
  - `03_Sessions/Phase_02_Development/SESSION-P2-0013_TASK-0009_Yaw0_Followup_Execution.md`
- Code paths inspected for this diagnosis:
  - `bsm/phase02/task09_runner.py`
  - `bsm/phase02/residual_solver.py`
  - `bsm/phase02/cue_bank.py`

## Diagnostic Conclusion

- The full-frequency `513` comparison-authority repair appears correct. The current failure is not explained by baseline drift.
- A direct full-`513` execution audit was also completed on `2026-04-22`:
  - targeted regression gate passed:
    - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_task09_runner bsm.tests.test_residual_solver`
    - result: `12` tests passed
  - one real-bundle full-`513` forward/backward audit passed:
    - selected yaw `0`
    - `run_bundle.c_magls.shape = [513, 5, 2]`
    - `solver_input_shape = [513, 5, 14]`
    - `fft_size = 1024`
    - `loss_mag`, `loss_dmag`, `loss_ild`, `loss_itd`, `loss_reg`, `loss_total` all remained finite
    - model gradients remained finite
  - one real-bundle full-`513` short smoke run passed:
    - `python -m bsm.phase02.task09_runner train ... --max-frequency-bins 513 --iterations 2`
    - required artifacts were emitted
    - `comparison_summary.json` was emitted under full `513`
    - retained metrics remained finite
    - therefore the current code path can execute on full `513` without an immediate numerical failure
- There is a real optimization-module bug:
  - `--include-front-end-energy-descriptor` is accepted into `ResidualSolverConfig`
  - but `bsm.phase02.task09_runner._build_solver_assets(...)` does not pass that flag into `build_solver_input_pack(...)`
  - therefore `T09-I3-y0-s3401` was not a real energy-descriptor ablation
  - the exact tie between `T09-I2-y0-s3401` and `T09-I3-y0-s3401` is consistent with that bug
- There is a major objective mismatch:
  - training `loss_ild` uses `compute_ild_loss_torch(...)`
  - that helper is explicitly a differentiable broadband ILD proxy, not the auditory ERB-band ILD metric exported by `build_cue_bank(...)`
  - the full-`513` audit shows that this loss remains numerically executable at the wider band
  - but executability is not the same as correctness for the paper-aligned objective
  - in the current artifacts, the training ILD proxy drops sharply while the exported ILD error gets much worse than baseline
- There is also a retention-policy mismatch:
  - `best_composite` and early stopping are driven by normalized training loss components
  - promotion decisions are supposed to depend on exported comparison metrics
  - therefore the run keeps the checkpoint that is best for the training proxy objective, not necessarily the checkpoint that is best under the authoritative comparison rule
- The reduced `129`-bin pilot setting is acceptable for smoke and plumbing checks, but it is not aligned with the cited paper for an ILD-first decision:
  - `129` bins at the current FFT configuration only cover approximately `0` to `4 kHz`
  - the cited paper evaluates ILD over approximately `1.5 kHz` to `20 kHz`
  - this repository currently runs at `32 kHz`, so the achievable paper-aligned upper bound is `16 kHz`
  - therefore the next ILD-focused rerun should use full `513` bins and treat the paper-aligned ILD emphasis band as approximately `1.5 kHz` to `16 kHz`

## Implication For The Baseline Rule

- Do not relax the baseline-beat rule yet.
- Reason 1:
  - the current code already emits a composite-based machine verdict in `comparison_summary.json`
  - current retained runs still fail even under that weaker composite rule
- Reason 2:
  - the present ILD optimization target is misaligned with the exported ILD acceptance metric
  - relaxing the acceptance rule before repairing that mismatch would hide a measurement problem inside policy
- Temporary policy for the next session:
  - keep `four_down_accept` as the promotion target
  - allow composite-only improvement to count only as a research signal, not as promotion authority

## Required Repairs Before Any New Official Screening

### Repair 1. Fix The Energy-Descriptor Plumbing

- Change `bsm.phase02.task09_runner` so `_build_solver_assets(...)` receives `solver_config`
- Pass `include_front_end_energy_descriptor=solver_config.include_front_end_energy_descriptor` into `build_solver_input_pack(...)`
- Ensure the same path is used by both `train` and `compare`
- Extend tests so a `TASK-0009` run with the flag enabled proves that the solver-input channel count changes

### Repair 2. Record Actual Solver-Input Metadata

- Add `solver_input_pack.to_summary()` or equivalent metadata to the `TASK-0009` manifest/export path
- The next session must be able to prove from artifacts whether the energy descriptor was actually present

### Repair 3. Align Retention With Authoritative Evaluation

- Keep `best_loss` and current normalized `best_composite` as training-side diagnostics only
- Add one authoritative retained criterion based on exported comparison metrics on the full selected-orientation bundle
- Early stopping should follow the same authoritative retained criterion used for promotion review
- The next retained checkpoint should be selected by the metric family that is actually used to judge baseline-beating

### Repair 4. Instrument Proxy Versus Authority Drift

- At each evaluation cadence, log both:
  - training-side proxy losses
  - authoritative cue-bank metrics
- Minimum required pair:
  - proxy `loss_ild`
  - exported `ild_error`
- If the repaired trace still shows proxy ILD decreasing while authoritative ILD increases, that is blocker-grade evidence against the current proxy design

### Repair 5. Replace Or Supplement The Current ILD Proxy

- Do not keep the current broadband ILD proxy as the only ILD training target for the next official screening
- Minimum acceptable replacement:
  - a differentiable frequency-aware ILD loss computed across direction and frequency bins
- Preferred direction:
  - band-pooled ILD approximation that is structurally closer to the cue-bank auditory ILD evaluation
- The next session does not need to reproduce the full auditory path exactly
- It does need to stop optimizing a proxy that currently improves while the authoritative ILD metric degrades

### Repair 6. Raise The ILD-Focused Pilot Resolution

- For the next diagnostic rerun, change `max_frequency_bins` from `129` to full `513`
- Do not keep a reduced pilot resolution as the authority for deciding whether ILD-focused optimization works
- The next ILD objective should be evaluated and, if possible, weighted over the paper-aligned high-frequency band:
  - lower bound approximately `1.5 kHz`
  - upper bound limited by current repository Nyquist, approximately `16 kHz`

## Predeclared Test Standard

Type:

- Optimization readiness plus metric-alignment repair

Preconditions:

- environment is `bsm_harness_py311`
- the repaired full-`513` comparison path remains the only comparison authority
- current `TASK-0009` artifacts remain available for before/after comparison

Required checks:

- targeted regression before edits:

```bash
conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_task09_runner bsm.tests.test_residual_solver
```

- full regression after edits:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

- one short diagnostic run must prove:
  - energy-descriptor on/off changes the solver-input contract when requested
  - authoritative evaluation metrics are logged during training rather than only after training
  - retained checkpoint selection can follow the new authoritative criterion
  - all exported metrics remain finite

- one ILD-focused diagnostic run at full `513` bins must answer:
  - does authoritative `ild_error` improve at any retained checkpoint relative to the yaw `0` baseline
  - if not, does the repaired trace still show proxy/authority divergence

## Next Session Execution Order

### Stage A. Regression Gate

```bash
conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_task09_runner bsm.tests.test_residual_solver
```

### Stage B. Optimization Plumbing Repair

- Edit:
  - `bsm/phase02/task09_runner.py`
  - `bsm/tests/test_task09_runner.py`
- Required outcome:
  - energy-descriptor ablation becomes real and artifact-visible

### Stage C. Retention And Eval Alignment Repair

- Edit:
  - `bsm/phase02/task09_runner.py`
  - tests as needed
- Required outcome:
  - evaluation cadence emits authoritative full-`513` metrics
  - retained checkpoint policy can follow authoritative comparison metrics

### Stage D. ILD Proxy Repair

- Edit:
  - `bsm/phase02/cue_bank.py` or `bsm/phase02/residual_solver.py`, depending on final placement
  - tests covering the new differentiable ILD objective
- Required outcome:
  - the default ILD loss is closer in structure to the exported ILD authority than the current broadband proxy

### Stage E. Full Regression Gate

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

### Stage F. Narrow Repaired Diagnostic

Recommended first repaired diagnostic:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-D1-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 300 \
  --learning-rate 0.0008 \
  --loss-profile balanced_norm_v1 \
  --eval-every 25 \
  --checkpoint-every 50 \
  --max-frequency-bins 513 \
  --hidden-dim 24 \
  --block-count 2 \
  --rank 4
```

Optional second repaired diagnostic only after the first run is clean:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-D2-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 300 \
  --learning-rate 0.0008 \
  --loss-profile paper_ild_guarded_v1 \
  --eval-every 25 \
  --checkpoint-every 50 \
  --max-frequency-bins 513 \
  --hidden-dim 24 \
  --block-count 2 \
  --rank 4 \
  --include-front-end-energy-descriptor
```

## Completion Gate

- The next session may close as repaired planning/execution authority only if all of the following are true:
  - the energy-descriptor path is proven real by test and artifact metadata
  - retained-checkpoint selection is aligned with authoritative exported metrics
  - the new diagnostic trace makes proxy-versus-authority behavior explicit
  - at least one repaired diagnostic run has been executed and archived
  - the session records one explicit decision:
    - reopen yaw `0` screening under the repaired objective
    - revisit yaw `90` under the same repaired policy
    - or open a blocker because the current loss family still fails after the repairs

## Expected Decision After The Next Session

- Most likely valid outcomes are:
  - one repaired rerun is justified because the previous evidence was polluted by objective/plumbing mismatch
  - or a blocker is justified because the repaired objective still cannot produce authoritative ILD improvement
- The next session should not spend compute on a new broad sweep before those repairs are closed.
