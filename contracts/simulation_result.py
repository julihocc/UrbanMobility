from dataclasses import dataclass
from typing import Any


@dataclass
class SimulationResult:
    model: Any
    metrics: dict[int, dict[str, Any]]
    spawned_agents: dict[int, dict[str, Any]]
    city: Any
    heatmaps: dict[str, Any] | None = None
