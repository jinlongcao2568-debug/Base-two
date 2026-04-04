# AX9S Product Boundaries

Derived from:
- `docs/baseline/AX9S_建设工程域权威文档_中国落地售卖增强版_V1.4_2026-04-02.md`

Conflict rule:
- This file records boundary enforcement for implementation and QA.
- If it conflicts with the baseline, the baseline wins.

## Boundary Rules

- Do not create a second fact surface outside stage 6.
- Do not let page, API, or downstream business layers rebuild top-level judgment.
- Do not package internal or permissioned material as public automatic hits.
- Do not expand customer-visible delivery fields outside registered contracts.
- Do not present automatic findings as legal or regulatory conclusions.

## Customer-Visible Boundary

- Customer delivery must stay within registered whitelist and blacklist contracts.
- Manual override must remain explicit; it cannot silently replace automatic output.
- Stage 7 to stage 9 remain consumers of formal stage-6 facts and may not redefine core judgment.

## Current Repository Boundary

- Formal contracts live only in `docs/contracts/`.
- Live execution governance lives only in `docs/governance/`.
- Baseline authority and execution manuals stay under `docs/baseline/`.
