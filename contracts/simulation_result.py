from dataclasses import dataclass
import json
from typing import Any


def _to_builtin(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_builtin(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_builtin(v) for v in value]
    if isinstance(value, set):
        return [_to_builtin(v) for v in sorted(value)]

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except Exception:
            pass

    return value


@dataclass
class SimulationResult:
    model: Any
    metrics: dict[int, dict[str, Any]]
    spawned_agents: dict[int, dict[str, Any]]
    city: Any
    heatmaps: dict[str, Any] | None = None

    def to_dict(
        self,
        include_metrics: bool = True,
        include_spawned_agents: bool = True,
        include_heatmaps: bool = True,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "city_shape": tuple(self.city.city_grid.shape),
            "n_agents": len(self.city.agents),
        }

        if include_metrics:
            data["metrics"] = _to_builtin(self.metrics)
        if include_spawned_agents:
            data["spawned_agents"] = _to_builtin(self.spawned_agents)
        if include_heatmaps:
            data["heatmaps"] = _to_builtin(self.heatmaps)

        return data

    def to_json(
        self,
        include_metrics: bool = True,
        include_spawned_agents: bool = True,
        include_heatmaps: bool = True,
        indent: int = 2,
    ) -> str:
        return json.dumps(
            self.to_dict(
                include_metrics=include_metrics,
                include_spawned_agents=include_spawned_agents,
                include_heatmaps=include_heatmaps,
            ),
            indent=indent,
        )
