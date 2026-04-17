---
Document_ID: DIST-0001
Title: ILD Auditory Python Path
Status: Draft
Phase: Phase_02_Development
Track: Session
Maturity: Consolidating
Related_Docs:
  - 03_Sessions/Phase_02_Development/SESSION-P2-0001_ILD_Python_Replication.md
  - 05_Experiments/EXP-0001_Auditory_ILD_Python/README.md
  - 07_References/Open_Source_Baselines/BAS-0002_ILD_Auditory_Method.md
  - 00_Governance/Manifest/MANI-02_Active_Focus.md
Last_Updated: 2026-04-17
Review_Required: Yes
---

# ILD Auditory Python Path

## Distilled Consensus

- The Matlab auditory ILD reference can be reproduced directly in Python because its core ERB-bank functions are pure formula and filter-cascade code.
- The exact replication path should live outside `07_References/` and be developed in the project work area.
- `bsm_harness_py311` remains the required Python environment for this work.
- `gammatone` is the closest installed Python library match to the Matlab API and is suitable as a numerical cross-check.
- `pyfilterbank` remains useful for understanding the imported `Array2Binaural` baseline, but it is not the strictest match to the Matlab script structure.

## Implementation Direction

- Promote the first Python replication as a formal experiment under `05_Experiments/`.
- Implement the ERB spacing, filter design, filterbank application, and bandwise ILD helpers with `numpy` and `scipy.signal.lfilter`.
- Add a smoke test that checks shape, coefficient parity against `gammatone`, and a deterministic ILD sanity case.
