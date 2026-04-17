---
Document_ID: SESSION-P2-0001
Title: ILD Python Replication Session
Status: Draft
Phase: Phase_02_Development
Track: Session
Maturity: Consolidating
Related_Docs:
  - 07_References/Open_Source_Baselines/BAS-0002_ILD_Auditory_Method.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
  - 05_Experiments/EXP-0001_Auditory_ILD_Python/README.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# ILD Python Replication Session

## Goal

- Determine whether the Matlab auditory ILD path in `ILD computer method/` can be reproduced in Python inside `bsm_harness_py311`.

## Inputs Read

- `07_References/Open_Source_Baselines/ILD computer method/plot_ILD_fig9.m`
- `07_References/Open_Source_Baselines/ILD computer method/AuditoryToolbox/ERBSpace.m`
- `07_References/Open_Source_Baselines/ILD computer method/AuditoryToolbox/MakeERBFilters.m`
- `07_References/Open_Source_Baselines/ILD computer method/AuditoryToolbox/ERBFilterBank.m`
- `07_References/Open_Source_Baselines/Array2Binaural/ild_itd_analysis/evaluate_ilds_itds.py`
- `07_References/Open_Source_Baselines/Array2Binaural/requirements.txt`

## Findings

- The Matlab ILD path depends on three pure Matlab functions for the ERB filterbank stage.
- Those three functions do not rely on the bundled MEX binaries.
- `Array2Binaural` already contains a Python ILD/ITD analysis path, but it uses `pyfilterbank.GammatoneFilterbank` and operates in a different style from the Matlab script.
- The conda environment `bsm_harness_py311` is present and contains `numpy`, `scipy`, `pyfilterbank`, and `gammatone`.
- The installed `gammatone` package exposes `make_erb_filters` and `erb_filterbank`, which mirror the Slaney/AuditoryToolbox API shape.

## Decision Candidate

- Create a project-side Python reimplementation of `ERBSpace`, `MakeERBFilters`, and `ERBFilterBank` with only `numpy` and `scipy`.
- Keep `gammatone` and `pyfilterbank` documented as reference libraries, not as the primary dependency for the exact replication path.

## Verification Notes

- The pure Python translation can be checked numerically against the installed `gammatone` implementation because it follows the same coefficient layout.
- A simple stereo scaling test can validate the ILD calculation path without needing the full BSM pipeline.
