---
Document_ID: BAS-0001
Title: Array2Binaural Baseline
Status: Stable
Phase: Phase_01_Discovery
Track: Reference
Maturity: Consolidating
Related_Docs:
  - 00_Governance/Manifest/MANI-00_Project_State.md
  - 06_Assets/Datasets/Index.md
  - 06_Assets/External_Dependencies/Index.md
  - 06_Assets/Generated_Artifacts/Index.md
  - 06_Assets/External_Dependencies/DEP-0001_Array2Binaural_Conda_Env.md
  - 07_References/Open_Source_Baselines/BAS-0002_ILD_Auditory_Method.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# Array2Binaural Baseline

## Location

- Codebase root: `07_References/Open_Source_Baselines/Array2Binaural/`

## Role

- Imported open-source baseline for study and distillation.
- Preserved as a reference tree, separate from formal project governance and architecture.

## Notes

- The imported tree appears to contain code, external assets, generated artifacts, and evaluation results together.
- Future work should register key datasets, dependencies, and artifacts into `06_Assets/`.
- Active Python development is expected to run inside the conda environment `bsm_harness_py311`.
- The imported `ild_itd_analysis/evaluate_ilds_itds.py` script computes ILD/ITD with `pyfilterbank`, which is useful as a baseline-side reference but is distinct from the strict AuditoryToolbox-style ILD replication path.
- The adjacent `ILD computer method/` folder should be treated as a supplemental Matlab-side evaluation reference, not merged into the imported upstream tree.
