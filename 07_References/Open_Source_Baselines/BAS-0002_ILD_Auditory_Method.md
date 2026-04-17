---
Document_ID: BAS-0002
Title: ILD Auditory Method Reference
Status: Draft
Phase: Phase_02_Development
Track: Reference
Maturity: Consolidating
Related_Docs:
  - 07_References/Open_Source_Baselines/Index.md
  - 07_References/Open_Source_Baselines/ILD computer method/plot_ILD_fig9.m
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 05_Experiments/EXP-0001_Auditory_ILD_Python/README.md
  - 01_Charter/Goals/CHAR-06_Phase_01_Execution_Plan.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# ILD Auditory Method Reference

## Location

- Method root: `07_References/Open_Source_Baselines/ILD computer method/`

## Role

- Matlab reference for ERB-band ILD computation used in binaural cue evaluation.
- Supplemental baseline for reproducing the ILD analysis logic outside the imported `Array2Binaural` tree.

## Core Method

The Matlab implementation in `plot_ILD_fig9.m` computes ILD by:

1. Building ERB center frequencies with `ERBSpace`.
2. Designing a Slaney-style gammatone filter bank with `MakeERBFilters`.
3. Filtering left/right HRIR or reproduced binaural signals with `ERBFilterBank`.
4. Summing per-band energy and computing bandwise ILD in dB.
5. Averaging ILD or ILD error across ERB bands.

## Python Feasibility

- The three key functions `ERBSpace.m`, `MakeERBFilters.m`, and `ERBFilterBank.m` are pure Matlab formula/code and do not rely on MEX binaries.
- This means the method can be reproduced directly in Python with `numpy` and `scipy.signal.lfilter`.
- If reuse is preferable to direct translation, the closest Python-side helpers are:
  - `gammatone`
  - `pyfilterbank` from the Git dependency already listed by `Array2Binaural`

## Current Project Status

- A project-side Python replication has been added under `05_Experiments/EXP-0001_Auditory_ILD_Python/`.
- That implementation matches the installed `gammatone` coefficient and filterbank outputs to numerical precision in the current smoke test.
- `pyfilterbank` remains relevant for reading the imported `Array2Binaural` evaluation scripts, but it is not treated as the strict Matlab-equivalent path here.

## Constraint

- Treat this folder as reference material.
- Do not place new project implementation code inside `ILD computer method/`.
- Any Python reimplementation should live in the main project work area and cite this reference.
