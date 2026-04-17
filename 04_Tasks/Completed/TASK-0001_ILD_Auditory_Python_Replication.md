---
Document_ID: TASK-0001
Title: ILD Auditory Python Replication
Status: Stable
Phase: Phase_02_Development
Track: Task
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Phase_02_Development/SESSION-P2-0001_ILD_Python_Replication.md
  - 03_Sessions/Distillations/DIST-0001_ILD_Auditory_Python_Path.md
  - 05_Experiments/EXP-0001_Auditory_ILD_Python/README.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# ILD Auditory Python Replication

## Scope

- Replicate the Matlab auditory ERB-band ILD building blocks in Python.
- Keep implementation outside the imported reference trees.
- Use the `bsm_harness_py311` environment aligned with `Array2Binaural`.

## Outcome

- Added a project-side experiment with:
  - pure Python `ERBSpace`, `MakeERBFilters`, and `ERBFilterBank` equivalents
  - helper functions for bandwise and averaged ILD computation
  - a smoke test runnable in `bsm_harness_py311`
- Recorded the decision path in Session and Distillation documents.
- Updated documentation to register the environment rule and the new ILD reference material.
