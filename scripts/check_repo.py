from __future__ import annotations

from governance_lib import GovernanceError, find_repo_root, load_task_registry, load_worktree_registry, task_map
from governance_repo_checks import run_repo_checks


def main() -> int:
    try:
        root = find_repo_root()
        registry = load_task_registry(root)
        tasks_by_id = task_map(registry)
        worktrees = load_worktree_registry(root)
        run_repo_checks(root, registry, tasks_by_id, worktrees)
        print("[OK] governance checks passed")
        return 0
    except GovernanceError as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
