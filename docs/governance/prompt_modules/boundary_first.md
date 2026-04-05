# Boundary First

Apply these rules before execution instructions.

- State forbidden actions before desired actions.
- Define what the agent must not infer, must not change, and must not claim.
- Stop when scope, authority, or required inputs are unclear.
- Do not extend permissions from one approved action to adjacent actions.
- Read the actual artifact before editing it; do not edit from memory.
- Prefer narrower execution over speculative convenience.

## Preferred Constraints

- `NEVER` create a second truth surface or second primary rule source.
- `DO NOT` expand beyond `allowed_dirs`.
- `CRITICAL` stop when successor choice or ownership is ambiguous.
- `CRITICAL` stop when the user request could imply a task switch without explicit evidence.
