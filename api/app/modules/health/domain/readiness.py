from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ReadinessResult:
    database: str
