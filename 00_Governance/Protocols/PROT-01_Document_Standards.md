---
Document_ID: PROT-01
Title: Document Standards
Status: Stable
Phase: Phase_01_Discovery
Track: Governance
Maturity: Stable
Related_Docs:
  - 00_Governance/Protocols/PROT-00_Core_Protocols.md
  - 00_Governance/Manifest/MANI-01_Module_Register.md
Last_Updated: 2026-03-23
Review_Required: No
---

# Document Standards

## Frontmatter template

```yaml
---
Document_ID: [unique id]
Title: [document title]
Status: [Draft | Stable | Legacy]
Phase: [Phase_01_Discovery | Phase_02_Development | Phase_03_Evaluation]
Track: [Governance | Charter | Architecture | Session | Task | Experiment | Asset | Reference | Review]
Maturity: [Exploration | Consolidating | Stable]
Related_Docs:
  - [path]
Last_Updated: [YYYY-MM-DD]
Review_Required: [Yes | No]
---
```

## Naming rules

- Use one `Index.md` per folder as the navigation surface.
- Use one document per topic, task, experiment, or decision where possible.
- Use stable IDs such as `DEC-0001`, `EXP-0001`, or `TASK-0001`.

## Linking rules

- Use repo-relative paths in `Related_Docs`.
- Update the local `Index.md` whenever a document is created, moved, or retired.
