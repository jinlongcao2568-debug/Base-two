# Tool Boundaries

- Match tools to scenarios instead of using every available tool by default.
- Do not mix tools that break auditability when one governed command is sufficient.
- Keep repository mutations inside governed scripts, tracked worktrees, or explicit patches.
- Preserve readable logs for branch switches, closeout, and successor activation.
- Use read-only gates before any continuation that might activate a successor.

## Minimum Expectations

- repository gates before roadmap continuation
- hygiene gates before autonomous continuation
- branch switching only on a clean worktree
- no hidden cleanup, stash, reset, or discard flows
