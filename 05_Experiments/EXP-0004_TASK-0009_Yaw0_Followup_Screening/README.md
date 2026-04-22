---
Document_ID: EXP-0004
Title: TASK-0009 yaw 0 Follow-up Screening
Status: Draft
Phase: Phase_02_Development
Track: Experiment
Maturity: Planning
Related_Docs:
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 05_Experiments/EXP-0003_TASK-0009_Planned_Optimization_Campaign/README.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0011_TASK-0009_Screening_Execution.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0012_TASK-0009_Yaw0_Followup_Planning.md
  - 07_References/Papers/Berebi 等 - 2025 - BSM-iMagLS ILD Informed Binaural Signal Matching for Reproduction with Head-Mounted Microphone Arra.pdf
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
Last_Updated: 2026-04-22
Review_Required: Yes
---

# TASK-0009 yaw 0 Follow-up Screening

## Purpose

- Execute the next narrow `TASK-0009` screening session with yaw `0` as the first priority.
- Use the current `task09_runner` route without redesigning the front-end or coefficient authority.
- Use the unified paper-aligned ILD metric now shared by training and exported evaluation.
- Test whether a paper-inspired loss emphasis and a few narrow initialization/model variants can produce a retained checkpoint that beats the yaw `0` baseline on all four exported errors.
- Keep long-run optimization blocked unless a yaw `0` profile first proves it is worth promoting.

## Why yaw `0` first

- yaw `0` is the static default coefficient authority already accepted in `TASK-0007A`.
- yaw `0` avoids the extra interpretation burden of rotation-specific selection while the loss-policy question is still open.
- The first official yaw `90` screening already showed the key failure mode clearly:
  - magnitude and NMSE can improve
  - ILD can still regress enough to lose the baseline comparison
- Therefore the next session should first answer a simpler question:
  - can the current solver family produce an actually useful retained result on yaw `0`

## Starting Authority

- Inherited route authority:
  - `06_Assets/Generated_Artifacts/TASK-0008/20260421T085524Z/`
- Previous official screening authority:
  - `05_Experiments/EXP-0003_TASK-0009_Planned_Optimization_Campaign/README.md`
- Previous official screening artifacts:
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P1-y90-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P2-y90-s3401/`
  - `06_Assets/Generated_Artifacts/TASK-0009/T09-P3-y90-s3401/`
- Current runner capabilities already available in workspace:
  - orientation selection through `--orientation-yaw-deg`
  - normalized loss schedules
  - checkpoint save and resume
  - comparison export
  - tunable solver config through:
    - `--learning-rate`
    - `--hidden-dim`
    - `--block-count`
    - `--rank`
    - `--alpha-init`
    - `--alpha-max`
    - `--include-front-end-energy-descriptor`

## yaw `0` Baseline To Beat

These values are the current saved-eMagLS / `BSM-MagLS` yaw `0` baseline in the workspace under the unified paper-aligned ILD metric and should be treated as the immediate comparison target for the follow-up session:

- `ild_error = 12.72058527441395`
- `itd_proxy_error = 0.02620715039960546`
- `normalized_magnitude_error = 0.47876036643371495`
- `nmse = 1.3708966970443726`
- `retained_composite_metric = 14.596449488291642`

Primary success target for this follow-up session:

- find at least one retained yaw `0` checkpoint for which all four exported errors are lower than the values above

Secondary success target if the primary target fails:

- find a paper-like retained yaw `0` checkpoint with:
  - `ild_error <= 11.5`
  - `itd_proxy_error <= 0.029`
  - `normalized_magnitude_error <= 0.52`
  - `nmse <= 1.45`

The secondary target is intentionally weaker than the primary target. It exists only because the cited paper shows that ILD can improve strongly while the other objective metrics remain only comparable rather than strictly better.

Metric-system note:

- these values are not numerically comparable to the pre-unification `TASK-0009` ILD values
- the current baseline uses the same paper-aligned banded ILD object as the training loss
- therefore any new follow-up decision must use the values in this document rather than the earlier pre-unification values

## Comparison And Optimization Authority Clarification

The authoritative optimization and comparison resolution for this follow-up is full-frequency `513` bins.

That means:

- written yaw `0` baseline thresholds in this document remain authoritative
- the next official follow-up should train on full `513` bins rather than reduced `129`-bin pilot bundles
- promotion decisions must use the unified paper-aligned ILD metric already embedded in the current codebase

## Paper Guidance To Translate Carefully

From `Berebi et al. 2025`:

- objective:
  - `DiMLS = DMLS + λ1 * DdMLS + λ2 * DILD`
- example weighting:
  - `λ = [0.4, 10]`
- learning rate:
  - `0.0008`
- allocated iterations:
  - `200`
- reported practical convergence in the shown example:
  - approximately `100` iterations
- the paper explicitly reports:
  - a significant ILD decrease
  - other errors staying relatively stable rather than all improving at once

Important translation note for this repository:

- the paper does not optimize the exact same full loss vector used in `task09_runner`
- our runtime includes:
  - `mag`
  - `dmag`
  - `ild`
  - `itd`
  - `reg`
- our training objective is normalized after warmup, so the paper weights cannot be copied numerically one-to-one
- however, the ILD term is now defined on the same paper-aligned banded frequency region used by exported evaluation
- therefore the new schedules below are an informed approximation, not a literal port

## Required Narrow Code Update Before Screening

Add the following loss profiles to `bsm/phase02/task09_runner.py` under `LOSS_PROFILES`.

`paper_ild_guarded_v1`

- warmup:
  - `mag = 0.40`
  - `dmag = 0.20`
  - `ild = 0.30`
  - `itd = 0.05`
  - `reg = 0.05`
- main:
  - `mag = 0.28`
  - `dmag = 0.17`
  - `ild = 0.45`
  - `itd = 0.05`
  - `reg = 0.05`
- final:
  - `mag = 0.22`
  - `dmag = 0.13`
  - `ild = 0.55`
  - `itd = 0.05`
  - `reg = 0.05`

`paper_ild_push_v1`

- warmup:
  - `mag = 0.35`
  - `dmag = 0.20`
  - `ild = 0.35`
  - `itd = 0.05`
  - `reg = 0.05`
- main:
  - `mag = 0.22`
  - `dmag = 0.13`
  - `ild = 0.55`
  - `itd = 0.05`
  - `reg = 0.05`
- final:
  - `mag = 0.15`
  - `dmag = 0.10`
  - `ild = 0.65`
  - `itd = 0.05`
  - `reg = 0.05`

`paper_ild_push_v2`

- warmup:
  - `mag = 0.35`
  - `dmag = 0.25`
  - `ild = 0.30`
  - `itd = 0.05`
  - `reg = 0.05`
- main:
  - `mag = 0.20`
  - `dmag = 0.20`
  - `ild = 0.50`
  - `itd = 0.05`
  - `reg = 0.05`
- final:
  - `mag = 0.15`
  - `dmag = 0.20`
  - `ild = 0.55`
  - `itd = 0.05`
  - `reg = 0.05`

Rationale:

- `paper_ild_guarded_v1` keeps more magnitude protection
- `paper_ild_push_v1` is the most aggressive ILD-first schedule
- `paper_ild_push_v2` restores more derivative-magnitude pressure to reduce the risk of rough spectral behavior

If the next session edits `LOSS_PROFILES`, it must rerun:

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

before and after the screening execution.

## Runtime Policy For This Follow-up

- Environment:
  - `conda activate bsm_harness_py311`
- Preferred learning rate for all screening runs:
  - `0.0008`
- Use full-frequency optimization:
  - `max_frequency_bins = 513`
- Keep the default retained criterion:
  - `best_composite`
- Keep early stop active:
  - `early_stop_patience = 4`
- Do not run a promoted long job unless one yaw `0` profile first meets the acceptance rule below.

## Acceptance Rule For This Follow-up

For each retained run, read `comparison_summary.json` and apply this order:

1. `four_down_accept`

- `ild_error < 12.72058527441395`
- `itd_proxy_error < 0.02620715039960546`
- `normalized_magnitude_error < 0.47876036643371495`
- `nmse < 1.3708966970443726`

2. `paper_like_accept`

- `ild_error <= 11.5`
- `itd_proxy_error <= 0.029`
- `normalized_magnitude_error <= 0.52`
- `nmse <= 1.45`

3. `reject`

- anything worse than the two rules above

Promotion rule:

- promote only a profile that reaches at least `paper_like_accept`
- if multiple profiles satisfy `paper_like_accept`, prefer:
  - first: `four_down_accept`
  - second: lower `ild_error`
  - third: lower retained composite metric
- if no profile satisfies `paper_like_accept`, record `no_promotion` again and do not launch a long run

## Historical Artifact Refresh Under The Unified Metric

Existing `TASK-0009` artifacts were refreshed against the current unified metric after the ILD-definition repair.

Refreshed observation:

- all compatible historical retained screening runs now beat the refreshed baseline on runner composite verdict
- however, none of those refreshed runs satisfy:
  - `four_down_accept`
  - `paper_like_accept`
- therefore the refreshed historical evidence is still not strong enough to grant promotion without a new official rerun
- special case:
  - `T09-I3-y0-s3401` was produced before the energy-descriptor plumbing repair
  - its checkpoint expects the old `14`-channel solver input while the repaired manifest now declares `15` channels
  - therefore it must be treated as an old-format historical artifact rather than as a refreshed comparison authority

## Execution Order

### Stage A. Regression Gate

```bash
conda run -n bsm_harness_py311 python -m unittest discover -s bsm/tests
```

### Stage B. Optional 200-Iteration Smoke

Use exactly one smoke after the new loss profiles are added:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-SM1-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 200 \
  --learning-rate 0.0008 \
  --loss-profile paper_ild_guarded_v1 \
  --eval-every 50 \
  --checkpoint-every 100 \
  --max-frequency-bins 513 \
  --hidden-dim 24 \
  --block-count 2 \
  --rank 4 \
  --alpha-init 0.15 \
  --alpha-max 0.35 \
  --indent 2
```

Smoke acceptance:

- no NaN or Inf in exported metrics
- `comparison_summary.json` exists
- no crash during checkpoint write

If the smoke fails, stop and fix the issue before the official screening.

### Stage C. Official Loss-Policy Screening On yaw `0`

All five runs below use the same solver shape and differ only in loss schedule.

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-P4-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 1200 \
  --learning-rate 0.0008 \
  --loss-profile balanced_norm_v1 \
  --eval-every 100 \
  --checkpoint-every 200 \
  --max-frequency-bins 513 \
  --hidden-dim 24 \
  --block-count 2 \
  --rank 4 \
  --alpha-init 0.15 \
  --alpha-max 0.35 \
  --indent 2
```

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-P5-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 1200 \
  --learning-rate 0.0008 \
  --loss-profile spatial_norm_v1 \
  --eval-every 100 \
  --checkpoint-every 200 \
  --max-frequency-bins 513 \
  --hidden-dim 24 \
  --block-count 2 \
  --rank 4 \
  --alpha-init 0.15 \
  --alpha-max 0.35 \
  --indent 2
```

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-P6-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 1200 \
  --learning-rate 0.0008 \
  --loss-profile paper_ild_guarded_v1 \
  --eval-every 100 \
  --checkpoint-every 200 \
  --max-frequency-bins 513 \
  --hidden-dim 24 \
  --block-count 2 \
  --rank 4 \
  --alpha-init 0.15 \
  --alpha-max 0.35 \
  --indent 2
```

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-P7-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 1200 \
  --learning-rate 0.0008 \
  --loss-profile paper_ild_push_v1 \
  --eval-every 100 \
  --checkpoint-every 200 \
  --max-frequency-bins 513 \
  --hidden-dim 24 \
  --block-count 2 \
  --rank 4 \
  --alpha-init 0.15 \
  --alpha-max 0.35 \
  --indent 2
```

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-P8-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 1200 \
  --learning-rate 0.0008 \
  --loss-profile paper_ild_push_v2 \
  --eval-every 100 \
  --checkpoint-every 200 \
  --max-frequency-bins 513 \
  --hidden-dim 24 \
  --block-count 2 \
  --rank 4 \
  --alpha-init 0.15 \
  --alpha-max 0.35 \
  --indent 2
```

After these five runs, select exactly one best loss profile by the acceptance rule above.

### Stage D. Narrow Initialization / Capacity Screening

Use the single best loss profile from Stage C and run the following three variants.

Conservative alpha start:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-I1-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 1200 \
  --learning-rate 0.0008 \
  --loss-profile <best_stage_c_profile> \
  --eval-every 100 \
  --checkpoint-every 200 \
  --max-frequency-bins 513 \
  --hidden-dim 24 \
  --block-count 2 \
  --rank 4 \
  --alpha-init 0.05 \
  --alpha-max 0.20 \
  --indent 2
```

Higher capacity:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-I2-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 1200 \
  --learning-rate 0.0008 \
  --loss-profile <best_stage_c_profile> \
  --eval-every 100 \
  --checkpoint-every 200 \
  --max-frequency-bins 513 \
  --hidden-dim 48 \
  --block-count 3 \
  --rank 8 \
  --alpha-init 0.15 \
  --alpha-max 0.35 \
  --indent 2
```

Higher capacity plus energy descriptor:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-I3-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 1200 \
  --learning-rate 0.0008 \
  --loss-profile <best_stage_c_profile> \
  --eval-every 100 \
  --checkpoint-every 200 \
  --max-frequency-bins 513 \
  --hidden-dim 48 \
  --block-count 3 \
  --rank 8 \
  --alpha-init 0.15 \
  --alpha-max 0.35 \
  --include-front-end-energy-descriptor \
  --indent 2
```

Select exactly one retained candidate after Stage D.

### Stage E. Stability Check Across Seeds

Only if the Stage D winner reaches at least `paper_like_accept`, rerun it with two new seeds.

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-S1-y0-s3402 \
  --orientation-yaw-deg 0 \
  --seed 3402 \
  --iterations 1200 \
  --learning-rate 0.0008 \
  --loss-profile <winning_profile> \
  --eval-every 100 \
  --checkpoint-every 200 \
  --max-frequency-bins 513 \
  --hidden-dim <winning_hidden_dim> \
  --block-count <winning_block_count> \
  --rank <winning_rank> \
  --alpha-init <winning_alpha_init> \
  --alpha-max <winning_alpha_max> \
  --indent 2
```

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-S2-y0-s3403 \
  --orientation-yaw-deg 0 \
  --seed 3403 \
  --iterations 1200 \
  --learning-rate 0.0008 \
  --loss-profile <winning_profile> \
  --eval-every 100 \
  --checkpoint-every 200 \
  --max-frequency-bins 513 \
  --hidden-dim <winning_hidden_dim> \
  --block-count <winning_block_count> \
  --rank <winning_rank> \
  --alpha-init <winning_alpha_init> \
  --alpha-max <winning_alpha_max> \
  --indent 2
```

Stability rule:

- if all three seeds remain at least `paper_like_accept`, the profile is stable enough to consider promotion
- if only the original seed passes, do not promote

### Stage F. Promotion Decision

Promote to a yaw `0` long run only if:

- one candidate reaches `four_down_accept`, or
- one candidate reaches `paper_like_accept` and passes the two-seed stability check

If promotion is granted, recommended long-run command:

```bash
conda run -n bsm_harness_py311 python -m bsm.phase02.task09_runner train \
  --run-id T09-R2-y0-s3401 \
  --orientation-yaw-deg 0 \
  --seed 3401 \
  --iterations 8000 \
  --learning-rate 0.0008 \
  --loss-profile <promoted_profile> \
  --eval-every 200 \
  --checkpoint-every 500 \
  --max-frequency-bins 513 \
  --hidden-dim <promoted_hidden_dim> \
  --block-count <promoted_block_count> \
  --rank <promoted_rank> \
  --alpha-init <promoted_alpha_init> \
  --alpha-max <promoted_alpha_max> \
  <optional_energy_descriptor_flag> \
  --early-stop-patience 8 \
  --indent 2
```

If promotion is not granted:

- record `no_promotion`
- do not launch a long run
- decide whether the next action should return to yaw `90`, add one more narrow loss profile, or open a blocker

## Comparison Extraction Command

After any batch of runs, use this command to print deltas against the yaw `0` baseline:

```bash
conda run -n bsm_harness_py311 python - <<'PY'
import json
from pathlib import Path

baseline = {
    "ild_error": 12.72058527441395,
    "itd_proxy_error": 0.02620715039960546,
    "normalized_magnitude_error": 0.47876036643371495,
    "nmse": 1.3708966970443726,
}

artifact_root = Path("06_Assets/Generated_Artifacts/TASK-0009")
for run_dir in sorted(artifact_root.glob("T09-*-y0-*")):
    summary_path = run_dir / "comparison_summary.json"
    if not summary_path.exists():
        continue
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    metric = payload["retained_metric_summary"]
    print(run_dir.name)
    for key, base in baseline.items():
        value = metric[key]
        print(f"  {key}: {value:.6f}  delta={value - base:+.6f}")
    print(f"  verdict={payload['concise_retention_verdict']}")
PY
```

## Required Documentation Update After Execution

After the next session completes, update:

- the new execution session note
- `05_Experiments/Registry/Result_Tracker.md`
- `06_Assets/Generated_Artifacts/Index.md`
- `00_Governance/Manifest/MANI-02_Active_Focus.md`
- `00_Governance/Manifest/MANI-03_Continuation_Authority.md`

## Explicit Non-Goals For This Follow-up

- no dynamic head-tracking implementation work
- no new orientation bank beyond the accepted yaw `0` and yaw `90`
- no broad all-combination hyperparameter search
- no claim that paper-level perceptual performance has been reproduced just because one screening run improves ILD
