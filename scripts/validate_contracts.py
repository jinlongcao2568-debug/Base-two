from __future__ import annotations

from contracts_validation_lib import (
    CONTRACT_BUNDLES,
    validate_authority_snippets,
    validate_contract_bundle,
    validate_handoff_catalog,
    validate_registry_files,
    main,
)


__all__ = [
    "CONTRACT_BUNDLES",
    "validate_authority_snippets",
    "validate_contract_bundle",
    "validate_handoff_catalog",
    "validate_registry_files",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
