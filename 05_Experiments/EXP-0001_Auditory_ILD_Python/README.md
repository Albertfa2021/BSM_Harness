---
Document_ID: EXP-0001
Title: Auditory ILD Python Replication
Status: Draft
Phase: Phase_02_Development
Track: Experiment
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Phase_02_Development/SESSION-P2-0001_ILD_Python_Replication.md
  - 03_Sessions/Distillations/DIST-0001_ILD_Auditory_Python_Path.md
  - 07_References/Open_Source_Baselines/BAS-0002_ILD_Auditory_Method.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Auditory ILD Python Replication

## Purpose

- Provide a project-side Python version of the auditory ILD building blocks referenced by `plot_ILD_fig9.m`.
- Keep the imported `ILD computer method/` directory read-only as source material.

## Files

- `code/auditory_ild.py`: pure `numpy` and `scipy` implementation of the Slaney-style ERB filterbank path.
- `code/smoke_test.py`: lightweight validation script for coefficient parity and ILD sanity.

## Current Method Scope

- `erb_space`: Matlab `ERBSpace` equivalent.
- `make_erb_filters`: Matlab `MakeERBFilters` equivalent.
- `erb_filter_bank`: Matlab `ERBFilterBank` equivalent.
- `compute_band_ild_db`: per-band ILD from left/right signals.
- `compute_mean_ild_db`: average ILD across ERB bands.
- `compute_mean_ild_error_db`: mean absolute ERB-band ILD error between reference and candidate binaural signals.

## Validation

Run in the dedicated environment:

```bash
conda activate bsm_harness_py311
python 05_Experiments/EXP-0001_Auditory_ILD_Python/code/smoke_test.py
```

The smoke test checks:

- ERB coefficient matrix shape
- numerical agreement with installed `gammatone` filter coefficients and filterbank outputs when available
- expected `6.0206 dB` ILD for a simple amplitude-ratio sanity case

## Library Position

- Exact replication path: the local pure Python implementation in `code/auditory_ild.py`
- Closest installed library match: `gammatone`
- Useful baseline-side library already used by `Array2Binaural`: `pyfilterbank`
