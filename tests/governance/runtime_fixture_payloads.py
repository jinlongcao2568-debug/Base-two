from __future__ import annotations

from typing import Any


def task_source_registry_payload() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": "2026-04-04T00:00:00+08:00",
        "sources": [
            {
                "source_id": "doc_local",
                "kind": "doc_local",
                "enabled": True,
                "implemented": True,
                "status": "active",
                "adapter": "doc_local_v1",
                "poll_mode": "on_demand",
                "unsupported_in_v1": False,
                "notes": "Repository-native coordination source.",
            },
            {
                "source_id": "linear",
                "kind": "linear",
                "enabled": False,
                "implemented": False,
                "status": "disabled",
                "adapter": "planned",
                "poll_mode": "not_configured",
                "unsupported_in_v1": True,
                "notes": "Reserved for future external intake.",
            },
            {
                "source_id": "github_issues",
                "kind": "github_issues",
                "enabled": False,
                "implemented": False,
                "status": "disabled",
                "adapter": "planned",
                "poll_mode": "not_configured",
                "unsupported_in_v1": True,
                "notes": "Reserved for future external intake.",
            },
            {
                "source_id": "jira",
                "kind": "jira",
                "enabled": False,
                "implemented": False,
                "status": "disabled",
                "adapter": "planned",
                "poll_mode": "not_configured",
                "unsupported_in_v1": True,
                "notes": "Reserved for future external intake.",
            },
        ],
    }


def worker_registry_payload() -> dict[str, Any]:
    return {
        "version": "1.0",
        "updated_at": "2026-04-04T00:00:00+08:00",
        "workers": [
            {
                "worker_id": "worker-local-01",
                "kind": "local",
                "enabled": True,
                "status": "active",
                "host": "localhost",
                "workspace_root": ".",
                "capabilities": ["coordination", "execution"],
                "unsupported_in_v1": False,
                "last_heartbeat_at": None,
                "notes": "Single-machine worker.",
            }
        ],
    }
