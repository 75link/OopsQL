from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum


class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    suggestion: str
    line: int | None = None
    excerpt: str | None = None

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        return {key: value for key, value in data.items() if value is not None}


@dataclass
class RiskReport:
    file: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def overall_risk(self) -> str:
        if not self.findings:
            return "LOW"
        return max(self.findings, key=lambda item: Severity[item.severity]).severity

    @property
    def findings_count(self) -> int:
        return len(self.findings)

    def to_dict(self) -> dict[str, object]:
        return {
            "file": self.file,
            "overall_risk": self.overall_risk,
            "findings_count": self.findings_count,
            "findings": [finding.to_dict() for finding in self.findings],
        }

