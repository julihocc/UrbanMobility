from typing import Any

from contracts.simulation_result import SimulationResult
from services.simulation_service import run_simulation_from_parameters


def run_exploration(
    parameters: dict[str, Any], include_heatmaps: bool = False
) -> SimulationResult:
    """Exploration-friendly wrapper around the application service."""
    return run_simulation_from_parameters(parameters, include_heatmaps=include_heatmaps)


def summarize_metrics(result: SimulationResult) -> dict[str, Any]:
    metrics = result.metrics
    if not metrics:
        return {
            "steps": 0,
            "arrivals": 0,
            "collisions": 0,
            "runovers": 0,
        }

    steps = len(metrics)
    arrivals = sum(len(step.get("arrivals", {})) for step in metrics.values())
    collisions = sum(len(step.get("collisions", [])) for step in metrics.values())
    runovers = sum(len(step.get("runovers", [])) for step in metrics.values())

    return {
        "steps": steps,
        "arrivals": arrivals,
        "collisions": collisions,
        "runovers": runovers,
    }
