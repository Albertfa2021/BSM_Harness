---
Document_ID: DEP-0001
Title: Array2Binaural Conda Environment
Status: Draft
Phase: Phase_02_Development
Track: Asset
Maturity: Consolidating
Related_Docs:
  - 06_Assets/External_Dependencies/Index.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 01_Charter/Goals/CHAR-06_Phase_01_Execution_Plan.md
  - Agent.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Array2Binaural Conda Environment

## Purpose

- Provide the dedicated Python development environment for work derived from `Array2Binaural`.
- Keep project development aligned with the baseline dependency set.

## Environment

- Conda env name: `bsm_harness_py311`
- Python version target: `3.11`
- Base dependency source: `07_References/Open_Source_Baselines/Array2Binaural/requirements.txt`

## Usage

- Create: `conda create -y -n bsm_harness_py311 python=3.11 pip`
- Activate: `conda activate bsm_harness_py311`
- Install baseline dependencies: `pip install -r 07_References/Open_Source_Baselines/Array2Binaural/requirements.txt`

## Current Status

- Environment `bsm_harness_py311` has been created.
- Core baseline packages required for current development have been verified by import, including `torch`, `pyroomacoustics`, `spaudiopy`, `pyfilterbank`, `h5py`, `librosa`, and `soundfile`.
- The environment has also been used to run `05_Experiments/EXP-0001_Auditory_ILD_Python/code/smoke_test.py` successfully.
- On `2026-04-17`, the environment-side `torch` runtime was repaired by:
  - removing the mixed conda `pytorch` install plus stale pip `torch` residue
  - installing the official `torch 2.5.1+cpu` wheel
  - restoring `llvm-openmp` so `libiomp5.so` is present in the env runtime
- Post-repair verification in `bsm_harness_py311` now includes:
  - `import torch`
  - finite backward pass on the cue-bank ITD helper test

## Notes

- `pyfilterbank` is not a normal PyPI package and is installed from the Git dependency declared by the baseline requirements file.
- `gammatone` is available from PyPI and is installed in the current environment as a validation helper for the auditory ILD replication path, but it is not part of the upstream `Array2Binaural/requirements.txt` base set.
- Some PyPI downloads in this environment required `--trusted-host pypi.org --trusted-host files.pythonhosted.org` due intermittent SSL EOF failures.
- New dependencies introduced during development should be recorded here before they become part of the working stack.
