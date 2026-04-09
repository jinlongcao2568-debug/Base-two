---
mvp_scope: stage2_to_stage6
included_stages:
- stage2
- stage3
- stage4
- stage5
- stage6
excluded_stages:
- stage1
- stage7
- stage8
- stage9
updated_at: '2026-04-09T10:30:00+08:00'
---

# AX9S MVP Scope

Derived from:
- `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md`

Conflict rule:
- This file expands MVP scope for execution planning.
- It does not replace the baseline authority document.

## Formal China MVP Scope

Included:
- Stage 2 public-source ingestion and public-chain discovery
- Stage 3 structured parsing
- Stage 4 rule validation and evidence-backed findings
- Stage 5 report and review outputs
- Stage 6 unified `project_fact`, sellability state, and downstream consumption object

Excluded from current MVP baseline:
- Stage 7 business-sales automation as a required shipping dependency
- Stage 8 contact automation as a required shipping dependency
- Stage 9 delivery automation as a required shipping dependency
- Any second truth layer outside stage 6

## MVP Acceptance Gates

- Formal contracts exist for the critical chain objects needed by MVP.
- `stage3 -> stage4 -> stage6` has a real integration regression path.
- Sellability and report-state enums remain pinned to the authority document.
- Governance, contracts, automation, and integration tests are repeatable from scripts.

## MVP Non-Claims

- No unattended all-day autonomous execution claim.
- No automatic legal conclusion claim.
- No customer-visible API or page may rebuild judgment outside `project_fact`.
