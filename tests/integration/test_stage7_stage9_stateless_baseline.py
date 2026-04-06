from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_stage7_stage9_stateless_baseline_pack_is_present() -> None:
    sql_path = ROOT / "db/migrations/001_stage7_stage9_stateless_baseline.sql"
    rollback_path = ROOT / "db/migrations/001_stage7_stage9_stateless_baseline.rollback.md"
    seed_path = ROOT / "db/migrations/001_stage7_stage9_stateless_baseline.seed.sql"

    assert sql_path.exists()
    assert rollback_path.exists()
    assert seed_path.exists()
    assert "creates no business tables" in sql_path.read_text(encoding="utf-8")
    assert "no persistent business objects" in rollback_path.read_text(encoding="utf-8").lower()
    assert "creates no persistent downstream objects" in seed_path.read_text(encoding="utf-8").lower()
