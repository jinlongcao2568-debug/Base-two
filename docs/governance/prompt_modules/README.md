# Prompt Modules

This directory is the governed prompt source of truth for AX9 automation roles.

Use these modules as composable inputs. Do not paste the entire historical memo into every system prompt. Load only the modules required by the active role and task boundary.

## Modules

- `boundary_first.md`
  - forbid unsafe actions before describing desired actions
- `reporting_discipline.md`
  - require factual updates, explicit uncertainty, and stop conditions
- `tool_boundaries.md`
  - tie each tool to explicit situations and audit rules
- `role_overrides.md`
  - role-specific overlays for coordinator, worker, and reviewer lanes

## Loading Rules

- coordinator
  - load boundary, reporting, and role override modules
- worker
  - load boundary, tool, and role override modules
- reviewer
  - load boundary, reporting, tool, and role override modules

## Governance Rules

- Prompt modules are live governance artifacts.
- Root-level scratch notes are not a live prompt source.
- If a module conflicts with `docs/product/AUTHORITY_SPEC.md` or `docs/governance/OPERATOR_MANUAL.md`, the formal governance documents win.
