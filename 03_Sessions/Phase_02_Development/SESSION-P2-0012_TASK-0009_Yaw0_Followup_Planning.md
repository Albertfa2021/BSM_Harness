---
Document_ID: SESSION-P2-0012
Title: TASK-0009 yaw 0 Follow-up Planning
Status: Stable
Phase: Phase_02_Development
Track: Session
Maturity: Planning
Related_Docs:
  - 00_Governance/Protocols/PROT-03_Session_Scoped_Subtask_Execution.md
  - 04_Tasks/Active/TASK-0009_Planned_Neural_Optimization_Campaign.md
  - 05_Experiments/EXP-0003_TASK-0009_Planned_Optimization_Campaign/README.md
  - 05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md
  - 03_Sessions/Phase_02_Development/SESSION-P2-0011_TASK-0009_Screening_Execution.md
  - 07_References/Papers/Berebi 等 - 2025 - BSM-iMagLS ILD Informed Binaural Signal Matching for Reproduction with Head-Mounted Microphone Arra.pdf
  - 00_Governance/Manifest/MANI-03_Continuation_Authority.md
Last_Updated: 2026-04-21
Review_Required: Yes
---

# TASK-0009 yaw 0 Follow-up Planning

## Target Subtask

- Convert the post-`SESSION-P2-0011` owner decision into an executable next-session protocol.
- Prioritize yaw `0` screening before any renewed yaw `90` work.
- Make the next session narrow, reproducible, and directly executable from written commands.

## Reason For The Shift

- The first official yaw `90` screening established the failure mode clearly:
  - improved magnitude-related metrics alone are not enough
  - ILD regression can still cause `baseline_not_beaten`
- The cited BSM-iMagLS paper shows that ILD can improve strongly while other errors remain only comparable.
- Therefore the next session should first answer the cleaner static-default question on yaw `0`:
  - can the current solver family produce a retained result that is clearly better than the saved-eMagLS baseline

## Outcome

- Opened `EXP-0004` as the next executable `TASK-0009` authority.
- Fixed the next-session posture:
  - start with yaw `0`
  - translate the paper loss emphasis carefully rather than literally
  - keep the search narrow:
    - a few loss schedules
    - a few initialization / capacity variants
    - a small seed stability check only if a promising candidate appears
- Declared two acceptance levels:
  - strict `four_down_accept`
  - weaker `paper_like_accept`

## Next Step

- The next execution session should follow:
  - `05_Experiments/EXP-0004_TASK-0009_Yaw0_Followup_Screening/README.md`
- It should not launch a long run unless the written acceptance rule is satisfied.
