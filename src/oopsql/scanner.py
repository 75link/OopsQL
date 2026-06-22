from __future__ import annotations

from pathlib import Path

from oopsql.config import OopsConfig, load_config
from oopsql.models import RiskReport
from oopsql.rules import analyze_sql


def scan_path(path: Path, config: OopsConfig | None = None) -> list[RiskReport]:
    config = config or load_config(path)
    if path.is_file():
        return [scan_file(path, config)]
    if path.is_dir():
        files = sorted(item for item in path.rglob("*.sql") if item.is_file())
        return [scan_file(file_path, config) for file_path in files]
    raise FileNotFoundError(f"Path not found: {path}")


def scan_file(path: Path, config: OopsConfig) -> RiskReport:
    sql = path.read_text(encoding="utf-8")
    return RiskReport(file=str(path), findings=analyze_sql(sql, config))

