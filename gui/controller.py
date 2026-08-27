from typing import Any

from contracts.simulation_result import SimulationResult
from gui.renderers import GuiRenderer
from services.simulation_service import run_simulation, run_simulation_from_parameters
from SimulationConfig import SimulationConfig


class SimulationController:
    def __init__(self, renderer: GuiRenderer):
        self.renderer = renderer
        self.last_result: SimulationResult | None = None

    def run(self, config: SimulationConfig, include_heatmaps: bool = True) -> None:
        try:
            self.last_result = run_simulation(config, include_heatmaps=include_heatmaps)
            self.renderer.render_simulation(self.last_result)
        except Exception as exc:
            self.renderer.render_error(str(exc))

    def run_from_parameters(
        self, parameters: dict[str, Any], include_heatmaps: bool = True
    ) -> None:
        try:
            self.last_result = run_simulation_from_parameters(
                parameters, include_heatmaps=include_heatmaps
            )
            self.renderer.render_simulation(self.last_result)
        except Exception as exc:
            self.renderer.render_error(str(exc))

    def last_result_json(self) -> str | None:
        if self.last_result is None:
            return None
        return self.last_result.to_json()
