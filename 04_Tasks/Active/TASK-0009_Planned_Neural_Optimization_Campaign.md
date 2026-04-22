---
Document_ID: TASK-0009
Title: Planned Neural Optimization Campaign
Status: Active
Phase: Phase_02_Development
Track: Task
Maturity: Planning
Related_Docs:
  - 04_Tasks/Active/TASK-0008_Orientation_Coefficient_Bank_And_Training_Path.md
  - 04_Tasks/Active/TASK-0007A_eMagLS_Coefficient_Parity_Blocker.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0009_Orientation_Training_Path_Smoke.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0010_TASK-0009_Optimization_Planning.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0012_TASK-0009_Yaw0_Followup_Planning.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0013_TASK-0009_Yaw0_Followup_Execution.md
  - 05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md
  - 04_Tasks/Completed/TASK-0006_Residual_Solver_Loss_Loop_And_Evaluation_Export.md
  - 01_Charter/Goals/20260324_BSM_Neural_Optimization_Plan.md
  - 02_Architecture/Logic/ARCH-07_Phase_02_Implementation_Blueprint.md
  - 02_Architecture/Logic/ARCH-08_Pre_Training_Correctness_Validation_Blueprint.md
  - 02_Architecture/Data/ARCH-04_Input_Output_Contracts.md
  - 02_Architecture/Interfaces/ARCH-06_Module_Interfaces.md
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# Planned Neural Optimization Campaign

## Purpose

`TASK-0009` is the first task allowed to run planned long-run neural optimization on the accepted orientation-aware training path.

Its job is not to redesign the route from `TASK-0008`. Its job is to turn that accepted route into a reproducible screening-first campaign that identifies which parameter settings are worth trying. Long-run optimization is still allowed, but whether it runs, and which profile earns it, must be decided by the screening result rather than being fixed in advance.

## Starting Point From TASK-0008

`TASK-0008` already established the following handoff state:

- the orientation-aware coefficient source is fixed
- yaw `0` and yaw `90` saved-reference route checks pass
- the solver input pack can be built from selected orientation entries
- the selected yaw `90` smoke run is machine-accepted
- `loss_reduced = true` has already been observed on the selected yaw `90` short run
- the accepted handoff artifacts are under:
  - `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/`

`TASK-0009` must reuse this route directly. It must not reopen coefficient-authority or solver-path design questions unless a new blocker appears.

## Core Task

`TASK-0009` has three core responsibilities:

- define a narrow screening campaign clearly enough that the tested parameter set is reproducible before execution starts
- identify which parameter profile is worth promoting to a long-run optimization run
- compare promoted runs against declared baselines with machine-readable artifacts and concise review conclusions

## Basic Requirements

### Requirement 1. Lock The Execution Route

- Use the `TASK-0008` accepted orientation-aware route as the execution authority.
- Do not replace the selected-orientation coefficient bank, solver input semantics, or export contract as part of routine optimization work.
- Any route redesign belongs in a new blocker or repair task, not inside normal `TASK-0009` runs.

### Requirement 2. Declare The Run Matrix Before Running

Before the first long-run job, `TASK-0009` must declare at least:

- selected orientation set
- run identifiers
- random seed policy
- iteration budget
- optimizer and learning-rate schedule
- loss weights
- coefficient/frequency limits, if any
- checkpoint cadence
- evaluation cadence
- comparison baselines

Minimum planning policy for the first accepted campaign:

- keep the first official campaign narrow and controlled
- start from the already accepted selected yaw `90` route
- add yaw `0` only if it is explicitly declared as a control run, not as an implicit default
- do not treat the first campaign as a broad combination search
- do not predeclare that a long-run job must happen before the screening result is reviewed

## Requirement 3. Preserve Reproducibility

Every formal run must record:

- `producer_task_id = TASK-0009`
- `producer_session_id`
- `run_config_ref`
- environment name
- random seed
- exact orientation selection
- artifact root

The project-side runtime remains:

- `bsm_harness_py311`

## Requirement 4. Produce Long-Run Artifacts

Required artifact root:

```text
06_Assets/Generated_Artifacts/TASK-0009/<run_id>/
```

Minimum required files per accepted run:

- `run_manifest.json`
- `summary.json`
- `loss_trace.jsonl`
- `comparison_summary.json`
- `checkpoints/`

Optional but expected once useful:

- `plots/`
- `listening_manifest.json`
- `notes.md`

## Requirement 5. Compare Against Declared Baselines

`TASK-0009` must not stop at “training completed.” It must judge whether the learned result is useful.

Required comparison targets:

- `BSM-MagLS`
- saved aligned-ypr eMagLS reference
- later BSM-iMagLS entries, when such entries become available in the project

Required comparison outputs:

- ILD error
- ITD proxy error
- normalized magnitude error
- NMSE
- run-to-run stability notes

## Requirement 6. Keep Scope Controlled

In scope:

- parameter screening
- long-run optimization only when screening shows it is worth promoting
- checkpointing
- run-matrix definition
- seed policy
- logging policy
- comparison summaries
- narrowly scoped orientation expansion when explicitly planned

Out of scope for the initial `TASK-0009` acceptance:

- real-time playback integration
- arbitrary-orientation generalization claims without declared evidence
- broad scene-grid expansion without first recording a stable baseline campaign
- silent changes to the accepted `TASK-0008` route contract
- large combination sweeps without first proving they are worth the compute cost

## Work Packages

### Work Package 1. Planning Package

Create the first official `TASK-0009` planning package containing:

- run matrix
- checkpoint cadence
- logging policy
- comparison policy
- artifact naming policy

### Work Package 2. First Controlled Campaign

Run a narrow screening campaign on the accepted selected-orientation route.

The first controlled campaign should answer one question clearly:

- which parameter profile, if any, is worth promoting to a long-run optimization run

### Work Package 3. Promotion Decision

After screening completes, record one of the following outcomes explicitly:

- promote one shortlisted profile to long-run optimization
- keep screening only and defer long-run execution because no profile is strong enough
- stop and open a blocker because the route or loss policy is not behaving acceptably

### Work Package 4. Comparative Review

For each accepted run, record:

- best checkpoint
- selected iteration or stopping point
- final comparison metrics against baselines
- whether the run should be retained, rerun, or superseded

### Work Package 5. Registry And Continuation Updates

After each accepted run, update:

- `05_Experiments/Registry/Result_Tracker.md`
- `06_Assets/Generated_Artifacts/Index.md`
- active manifests, if the focus changes

## Predeclared Test Standard

Type:

- Reproducible planned optimization plus formal baseline comparison

Preconditions:

- `TASK-0008` machine-side acceptance is recorded
- `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/` exists
- `conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests` passes
- the selected run matrix is written before long-run execution begins

Required checks:

- run matrix is declared before execution
- every accepted run writes the required artifact files
- at least one checkpoint can be identified as the retained result
- all exported metrics are finite
- comparison summary covers the declared baselines
- continuation docs can identify the current best run without replaying the entire history

Completion gate:

- one `TASK-0009` planning session records the official screening matrix and logging policy
- at least one screening sweep is executed
- if screening promotes a profile, the promoted long-run job is executed and retained
- if screening does not promote a profile, the session records that decision explicitly rather than forcing a long-run run
- accepted artifacts are indexed
- the session records whether the run is strong enough to justify expansion to more orientations, scenes, or loss variants

## Outcome Target

If `TASK-0009` succeeds, the project should have:

- one official planned screening authority
- one reproducible shortlist and, only if justified by screening, one promoted long-run run
- one checkpointed artifact trail
- one baseline comparison summary that can support the next research or engineering decision

## 2026-04-21 Follow-up Direction

After `SESSION-P2-0011`, the official first screening matrix is complete and remains authoritative.

The next planned follow-up is intentionally narrower than a fresh broad campaign:

- use yaw `0` as the first follow-up orientation
- treat the paper-aligned ILD emphasis as a loss-policy hint, not a literal numeric port
- prefer finding one retained checkpoint that reduces all four exported errors against the yaw `0` baseline
- allow a weaker paper-like ILD-first acceptance only if the session records that compromise explicitly

The current executable authority for that follow-up is:

- `03_Sessions/Phase_02_Development/SESSION-P2-0012_TASK-0009_Yaw0_Followup_Planning.md`
- `05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md`

## 2026-04-21 Follow-up Execution Result

`SESSION-P2-0013` executed the written yaw `0` follow-up in `EXP-0004`.

Recorded outcome:

- the required `EXP-0004` loss profiles were added to `bsm.phase02.task09_runner`
- smoke `T09-SM1-y0-s3401` passed runtime/export integrity checks
- Stage C and Stage D both completed with retained artifacts under `06_Assets/Generated_Artifacts/TASK-0009/`
- under the repaired full-`513` authority, best Stage C retained run remains `T09-P4-y0-s3401` with `retained_composite = 15.37894172009149`
- best Stage D retained runs are `T09-I2-y0-s3401` and `T09-I3-y0-s3401`, tied at `15.417732386776184`
- no retained run reached `four_down_accept`
- no retained run reached `paper_like_accept`
- explicit decision remains `no_promotion`

Resolved comparison-authority decision:

- owner selected full-frequency `513` as the required comparison authority
- `task09_runner` comparison export was repaired so sliced pilot runs are evaluated against full selected-orientation baselines
- existing `TASK-0009` `comparison_summary.json` artifacts were refreshed with the repaired authority
- therefore the next `TASK-0009` step is no longer comparison-authority repair; it is deciding whether rerunning `yaw 0`, revisiting `yaw 90`, or opening a blocker is justified under the repaired policy
