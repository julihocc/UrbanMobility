from abc import ABC, abstractmethod

from contracts.simulation_result import SimulationResult


class GuiRenderer(ABC):
    @abstractmethod
    def render_simulation(self, result: SimulationResult) -> None:
        """Render a completed simulation result in the GUI."""

    @abstractmethod
    def render_error(self, message: str) -> None:
        """Render an error message in the GUI."""
