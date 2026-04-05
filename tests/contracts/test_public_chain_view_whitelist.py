from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml

from src.shared.contracts.public_chain_contract import PUBLIC_CHAIN_VIEW_FIELDS


def test_public_chain_view_fields_stay_within_customer_whitelist() -> None:
    whitelist = yaml.safe_load((ROOT / "docs/contracts/customer_delivery_field_whitelist.yaml").read_text(encoding="utf-8"))
    allowed_fields = {
        item["field"]
        for group in whitelist["allowlist"].values()
        for item in group
    }

    assert set(PUBLIC_CHAIN_VIEW_FIELDS).issubset(allowed_fields)
