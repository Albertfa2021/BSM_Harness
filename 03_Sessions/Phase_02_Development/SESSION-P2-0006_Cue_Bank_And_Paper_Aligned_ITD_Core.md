---
Document_ID: SESSION-P2-0006
Title: Cue Bank And Paper Aligned ITD Core
Status: Draft
Phase: Phase_02_Development
Track: Session
Maturity: Consolidating
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Completed/TASK-0005_Cue_Bank_And_Paper_Aligned_ITD_Core.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 05_Experiments/EXP-0001_Auditory_ILD_Python/README.md
  - 07_References/Papers/Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf
  - 03_Sessions/Distillations/DIST-0006_TASK-0005_Closure_And_TASK-0006_Handoff.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Cue Bank And Paper Aligned ITD Core

## Target Subtask

- Execute `TASK-0005` as the next Phase 02 implementation closure.
- Limit the session to:
  - cue-bank integration of the existing auditory ILD path
  - one paper-aligned differentiable ITD core

## Reference Anchors

- `05_Experiments/EXP-0001_Auditory_ILD_Python/code/auditory_ild.py`
- `07_References/Papers/Interaural_Time_Difference_Loss_for_Binaural_Target_Sound_Extraction.pdf`
- `02_Architecture/Data/ARCH-04_Input_Output_Contracts.md`
- `02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md`
- `02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md`

## Test Standard

### Scope

- The session changes only the cue-bank and paper-aligned ITD core boundary.

### Preconditions

- `conda run -n bsm_harness_py311 python -m bsm.phase02.baseline_renderer smoke` passes.
- Active environment must be `bsm_harness_py311`.
- The session must not add residual solver code.

### Shape And Contract Checks

- The cue module must expose reusable ILD and ITD helper outputs under one response-domain interface.
- ILD helper outputs must remain aligned with the current auditory replication semantics.
- ITD helper outputs must return GCC-PHAT cross-correlation sequences inside the configured `[-tau, tau]` window.

### Numerical And Stability Checks

- ILD outputs must be finite.
- ITD helper outputs and ITD loss must be finite.
- If implemented in differentiable code, one backward pass must remain finite.

### Acceptance Checks

- One smoke command runs ILD and ITD helpers on simple binaural examples and passes.
- The session records `tau`, sample rate, and any low-frequency gating choices explicitly.

## Completion Gate

- The session closes only after the predeclared cue-bank smoke command has been run and the result has been recorded here.

## Expected Deliverables

- One project-side cue module entry.
- One paper-aligned ITD helper path.
- One smoke path for ILD and ITD verification.

## Session Start State

- `TASK-0004` baseline renderer smoke passed on `2026-04-17`.
- Baseline-renderer authority remains `bsm.phase02.baseline_renderer`.
- Implementation started and was completed in this session note.

## Implementation Notes

- Added project-side cue authority in `bsm.phase02.cue_bank`.
- The cue module now accepts one response-domain contract:
  - reference response `[d, f, e]`
  - estimated response `[d, f, e]`
- The module promotes the existing ILD experiment into the formal cue path by loading:
  - `05_Experiments/EXP-0001_Auditory_ILD_Python/code/auditory_ild.py`
- The ITD path follows the paper-side GCC-PHAT definition:
  - compute GCC-PHAT cross-correlation coefficients
  - center the sequence
  - crop the configured `[-tau, tau]` lag window
  - compute sequence-domain MSE as `itd_proxy_error`
- Added optional ITD low-frequency prefilter support through `itd_lowpass_cutoff_hz`.
- Accepted default configuration in this session:
  - `sample_rate_hz = 32000`
  - `tau = 0.001 s`
  - `tau_samples = 32`
  - low-frequency gating disabled
- Added CLI entry points for:
  - `python -m bsm.phase02.cue_bank report`
  - `python -m bsm.phase02.cue_bank smoke`
- Added unit coverage in `bsm.tests.test_cue_bank`.
- Added a torch-backed helper entry for the differentiable ITD loss path:
  - `compute_itd_loss_torch`
- The later environment repair on `2026-04-17` removed the previous torch runtime blocker inside `bsm_harness_py311`.

## Verification Results

### Command 1

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.baseline_renderer smoke
```

- Result:
  - passed
  - reused as the recorded `TASK-0005` prerequisite gate

### Command 2

```bash
conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_baseline_renderer bsm.tests.test_cue_bank
```

- Result:
  - passed
  - `8` tests ran successfully
- Coverage focus:
  - baseline renderer regression guard
  - cue-bank shape and finiteness checks
  - `tau` window length enforcement
  - synthetic smoke coverage for ILD and ITD helper outputs
  - finite backward coverage for the torch-backed ITD helper path

### Command 3

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank smoke
```

- Result:
  - passed
  - ran ILD and ITD helpers on simple binaural examples
- Recorded smoke configuration:
  - `sample_rate_hz = 32000`
  - `tau = 0.001 s`
  - `tau_samples = 32`
  - low-frequency gating: disabled
- Recorded smoke shapes:
  - `ild_ref`: `[29, 2]`
  - `ild_est`: `[29, 2]`
  - `gcc_phat_ref`: `[2, 65]`
  - `gcc_phat_est`: `[2, 65]`
- Numerical summary:
  - all cue tensors remained finite
  - `ild_error_db = 0.8663306091661308`
  - `itd_proxy_error = 0.030767516417903505`

### Command 4

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.cue_bank report --baseline-name BSM-MagLS
```

- Result:
  - passed
  - ran the cue bank on the project-side `BSM-MagLS` response versus `h`
- Recorded report shapes:
  - `ild_ref`: `[29, 72]`
  - `ild_est`: `[29, 72]`
  - `gcc_phat_ref`: `[72, 65]`
  - `gcc_phat_est`: `[72, 65]`
- Numerical summary:
  - all cue tensors remained finite
  - `ild_error_db = 7.055816821140449`
  - `itd_proxy_error = 0.01563140569865554`

### Command 5

```bash
conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_cue_bank.CueBankTests.test_torch_itd_loss_supports_finite_backward_pass
```

- Result:
  - passed
  - executed inside the official project conda environment after the torch runtime repair
- Purpose:
  - close the remaining optimization-readiness acceptance item for `TASK-0005`
  - confirm that the differentiable ITD helper keeps a finite backward pass in `bsm_harness_py311`

## Completion Gate Result

- The predeclared `TASK-0005` cue-bank smoke command now exists and passes.
- The session-level completion gate for `TASK-0005` is satisfied.

## Next-Step Readiness

- The project-side cue bank and paper-aligned ITD core are now stable enough for `TASK-0006` to consume.
- The next implementation boundary is:
  - solver input assembly
  - residual solver
  - loss loop
  - evaluation export

## Follow-Up Environment Repair

- A later environment-maintenance pass on `2026-04-17` repaired the `bsm_harness_py311` torch runtime.
- Repair steps:
  - removed the mixed conda `pytorch` and stale pip `torch` residue
  - installed the official `torch 2.5.1+cpu` wheel
  - restored `llvm-openmp`, which recreated `libiomp5.so`
- Follow-up verification after the repair:
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_cue_bank.CueBankTests.test_torch_itd_loss_supports_finite_backward_pass`
  - `conda run -n bsm_harness_py311 python -m unittest bsm.tests.test_baseline_renderer bsm.tests.test_cue_bank`
- The backward check now passes inside the project conda environment and is no longer a runtime blocker.
- The earlier environment-limited note for `TASK-0005` can now be treated as closed.
