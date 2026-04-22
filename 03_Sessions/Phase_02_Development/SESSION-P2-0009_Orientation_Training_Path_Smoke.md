---
Document_ID: SESSION-P2-0009
Title: Orientation Training Path Smoke
Status: Stable
Phase: Phase_02_Development
Track: Session
Maturity: Consolidating
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0008_Orientation_Coefficient_Bank_And_Training_Path.md
  - 04_Tasks/Active/TASK-0007A_eMagLS_Coefficient_Parity_Blocker.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0008_Pre_Training_Correctness_Validation.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# Orientation Training Path Smoke

## Target Subtask

- Execute the machine-side acceptance run for `TASK-0008`.
- Limit the session to:
  - selected-orientation solver-path execution
  - short-run optimization quality judgment
  - artifact export
  - continuation-document updates

## Reference Anchors

- `04_Tasks/Active/TASK-0008_Orientation_Coefficient_Bank_And_Training_Path.md`
- `04_Tasks/Active/TASK-0007A_eMagLS_Coefficient_Parity_Blocker.md`
- `02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md`
- `02_Architecture/Data/ARCH-04_Input_Output_Contracts.md`
- `02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md`

## Test Standard

### Scope

- Validate the selected yaw `90` route from orientation-bank entry through solver input, short-run optimization, and machine-readable export.
- Do not start large-scale planned optimization in this session.

### Preconditions

- `TASK-0007A` repaired yaw `0` / yaw `90` saved-reference authority.
- `select_orientation_coefficients(..., yaw_deg=90)` returns the saved yaw `90` coefficient entry.
- `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests` is runnable.

### Acceptance Checks

- The selected orientation smoke must export `summary.json`, `loss_trace.jsonl`, and `orientation_training_path.json`.
- The summary must include `selected_orientation`, `orientation_bank_yaws_deg`, and solver-input metadata.
- The short-run quality conclusion must record whether loss actually decreases.

## Session Start State

- The earlier retained-reference run under `06_Assets/Generated_Artifacts/TASK-0008/20260421T065237Z/` proved the path was finite and traceable, but its short run did not reduce loss.
- A second machine run under `06_Assets/Generated_Artifacts/TASK-0008/20260421T085136Z/` still selected iteration `0` as best when using the original `4`-step / `1e-2` smoke schedule.
- The next action for this session was therefore to lengthen the run slightly and lower the step size until the short-run metric showed an actual decrease instead of simple stability.

## 2026-04-21 Parameter Sweep

- `iterations = 16`, `learning_rate = 0.002`
  - `initial_loss_total = 3.431663990020752`
  - `final_loss_total = 3.132002353668213`
  - `loss_reduced = true`
- `iterations = 24`, `learning_rate = 0.001`
  - `initial_loss_total = 3.445584535598755`
  - `final_loss_total = 3.062898874282837`
  - `loss_reduced = true`
- `iterations = 32`, `learning_rate = 0.0005`
  - `initial_loss_total = 3.446808099746704`
  - `final_loss_total = 3.1833455562591553`
  - `loss_reduced = true`

## Official Acceptance Run

- Commands:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver smoke --orientation-yaw-deg 90 --iterations 24 --learning-rate 0.001 --max-frequency-bins 65 --max-coefficients 96 --hidden-dim 24 --block-count 2 --rank 4 --indent 2
```

- Regression result:
  - `30` tests passed.

- Orientation-aware smoke result:
  - `ok = true`
  - `initial_loss_total = 3.4457359313964844`
  - `final_loss_total = 3.0254967212677`
  - `selected_iteration = 24`
  - `loss_reduced = true`
  - `normalized_magnitude_error = 0.34547776114508993`
  - `nmse = 1.636918544769287`
  - `ild_error = 9.372719879973232`
  - `itd_proxy_error = 0.018850489522542212`
  - `task09_ready = true`

- Export artifacts:
  - `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/summary.json`
  - `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/loss_trace.jsonl`
  - `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/orientation_training_path.json`

## Quality Conclusion

- `TASK-0008` now has an explicit short-run optimization quality result with actual loss reduction on the selected yaw `90` route.
- The selected-orientation training path is accepted as machine-ready for handoff to `TASK-0009`.
- Large-scale planned optimization is still not authorized in this session; `TASK-0009` must define the run matrix, logging policy, and checkpoint strategy.
