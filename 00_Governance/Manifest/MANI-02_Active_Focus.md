---
Document_ID: MANI-02
Title: Active Focus
Status: Draft
Phase: Phase_01_Discovery
Track: Governance
Maturity: Exploration
Related_Docs:
  - 04_Tasks/Active/Index.md
  - 03_Sessions/Phase_01_Discovery/Index.md
  - 07_References/Open_Source_Baselines/BAS-0001_Array2Binaural.md
  - 07_References/Open_Source_Baselines/BAS-0002_ILD_Auditory_Method.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Active Focus

## Current questions

- What is the internal pipeline of the imported Array2Binaural reference code?
- Which scripts are core reproduction scripts versus supporting utilities?
- Which artifacts should be promoted into explicit asset records?
- How should the Matlab-side ILD auditory method be mirrored in Python for the Phase 01 evaluation path?
- Which parts of the baseline stack must remain in the verified `bsm_harness_py311` environment for active development?

## Immediate next actions

- Read and summarize the imported reference codebase.
- Distill the ILD auditory reference method into the Python evaluation path.
- Keep dependency and asset records synchronized with the working environment.
- Create tasks and experiment records as concrete implementation work starts.
