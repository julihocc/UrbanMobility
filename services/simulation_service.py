from typing import Any

from SimulationConfig import SimulationConfig
from contracts.simulation_result import SimulationResult
from model.UrbanModelling import CityModel
from utils.Reporting import load_heatmaps


def run_simulation(
    config: SimulationConfig,
    model_cls: type[CityModel] = CityModel,
    include_heatmaps: bool = False,
) -> SimulationResult:
    return run_simulation_from_parameters(
        config.to_parameters(), model_cls=model_cls, include_heatmaps=include_heatmaps
    )


def run_simulation_from_parameters(
    parameters: dict[str, Any],
    model_cls: type[CityModel] = CityModel,
    include_heatmaps: bool = False,
) -> SimulationResult:
    model = model_cls(parameters)
    model.run()

    heatmaps = load_heatmaps(model) if include_heatmaps else None
    return SimulationResult(
        model=model,
        metrics=model.metrics,
        spawned_agents=model.spawned_agents,
        city=model.city,
        heatmaps=heatmaps,
    )
