---
Document_ID: PROT-00
Title: Core Protocols
Status: Stable
Phase: Phase_01_Discovery
Track: Governance
Maturity: Stable
Related_Docs:
  - 00_Governance/Manifest/MANI-00_Project_State.md
  - 00_Governance/Decisions/Index.md
  - 03_Sessions/Distillations/Index.md
Last_Updated: 2026-03-23
Review_Required: No
---

# Core Protocols

## P1. Document size

Any Markdown document must stay below 1000 lines. If a document approaches the limit, split it by topic and register the split in the local `Index.md`.

## P2. Mandatory frontmatter

All project documents must include standard frontmatter.

## P3. Bootstrap sequence

At the start of each work session, the agent must read:

1. `00_Governance/Protocols/PROT-00_Core_Protocols.md`
2. `00_Governance/Manifest/MANI-00_Project_State.md`

## P4. Session isolation

Session notes are exploratory. They must not directly overwrite charter or architecture documents.

## P5. Distillation before commit

Any formal update to `01_Charter/`, `02_Architecture/`, `05_Experiments/`, or `00_Governance/Manifest/` must be based on an explicit distillation record in `03_Sessions/Distillations/`.

## P6. Decision logging

Major reversals, scope changes, or logic changes must be recorded in `00_Governance/Decisions/`.

## P7. Traceability

Formal documents must reference their source sessions, distillations, experiments, or decisions when applicable.

## P8. Role separation

- `03_Sessions/`: raw thinking and discussion.
- `03_Sessions/Distillations/`: extracted consensus.
- `00_Governance/Decisions/`: major commitments and reversals.
- `01_Charter/` and `02_Architecture/`: current accepted state.
- `05_Experiments/`: evidence and analysis.
