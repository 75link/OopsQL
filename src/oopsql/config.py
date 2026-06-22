from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG = {
    "protected_tables": [
        "invoice",
        "invoiceitem",
        "payment",
        "glentry",
        "inventory",
        "client",
        "purchaseorder",
    ],
    "risky_keywords": ["production", "finance", "revenue", "accounting"],
    "require_transaction_for": [
        "UPDATE",
        "DELETE",
        "MERGE",
        "INSERT",
        "ALTER",
        "DROP",
        "TRUNCATE",
    ],
}


@dataclass(frozen=True)
class OopsConfig:
    protected_tables: list[str] = field(default_factory=list)
    risky_keywords: list[str] = field(default_factory=list)
    require_transaction_for: list[str] = field(default_factory=list)


def load_config(start_path: Path | None = None) -> OopsConfig:
    path = find_config(start_path or Path.cwd())
    if path is None:
        return config_from_dict(DEFAULT_CONFIG)

    return load_config_file(path)


def load_config_file(path: Path) -> OopsConfig:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    merged = {**DEFAULT_CONFIG, **data}
    return config_from_dict(merged)


def find_config(start_path: Path) -> Path | None:
    current = start_path if start_path.is_dir() else start_path.parent
    for directory in [current, *current.parents]:
        candidate = directory / "oopsql.yml"
        if candidate.exists():
            return candidate
    return None


def write_default_config(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"{path} already exists")
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(DEFAULT_CONFIG, handle, sort_keys=False)


def config_from_dict(data: dict[str, Any]) -> OopsConfig:
    return OopsConfig(
        protected_tables=[str(item).lower() for item in data.get("protected_tables", [])],
        risky_keywords=[str(item).lower() for item in data.get("risky_keywords", [])],
        require_transaction_for=[
            str(item).upper() for item in data.get("require_transaction_for", [])
        ],
    )
