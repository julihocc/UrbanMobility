from dataclasses import dataclass
from typing import Any, Callable


def _default_driver_weight() -> int:
    return 1


def _default_walker_weight() -> int:
    return 1


def _default_driver_maxspeed() -> int:
    return 60


def _default_walker_maxspeed() -> int:
    return 10


@dataclass
class SimulationConfig:
    seed: int = 0
    debug: bool = False
    city_grid: Any = None
    initial_walker_count: int = 0
    initial_driver_count: int = 0
    obstacles: Any = None
    potholes: Any = None
    driver_weight: Callable[[], int] = _default_driver_weight
    walker_weight: Callable[[], int] = _default_walker_weight
    driver_maxspeed: Callable[[], int] = _default_driver_maxspeed
    walker_maxspeed: Callable[[], int] = _default_walker_maxspeed
    repopulate: bool = False
    steps: int | None = None
    display: bool = False
    max_walker_spawn: int | None = None
    max_driver_spawn: int | None = None

    def to_parameters(self) -> dict[str, Any]:
        parameters = {
            "seed": self.seed,
            "debug": self.debug,
            "city_grid": self.city_grid,
            "initial_walker_count": self.initial_walker_count,
            "initial_driver_count": self.initial_driver_count,
            "obstacles": self.obstacles,
            "potholes": self.potholes,
            "driver_weight": self.driver_weight,
            "walker_weight": self.walker_weight,
            "driver_maxspeed": self.driver_maxspeed,
            "walker_maxspeed": self.walker_maxspeed,
            "repopulate": self.repopulate,
            "steps": self.steps,
            "display": self.display,
            "max_walker_spawn": self.max_walker_spawn,
            "max_driver_spawn": self.max_driver_spawn,
        }
        return {key: value for key, value in parameters.items() if value is not None}
