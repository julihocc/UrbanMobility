"""Quickstart: Run one simulation through the service layer.

Shows the recommended path for running a simulation using the application service API.
"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from SimulationConfig import SimulationConfig
from notebooks_support import summarize_metrics
from services import run_simulation
from utils.UrbanUtils import gen_city, gen_obstacles


def main():
    seed = 7
    random.seed(seed)
    city_grid = gen_city(block_shape=(12, 12), city_shape=(2, 2), street_parking=False, two_way=True, crop=0)
    obstacles, potholes = gen_obstacles(city_grid, obstacles=0.01, potholes=0.01)

    config = SimulationConfig(
        seed=seed,
        city_grid=city_grid,
        initial_walker_count=20,
        initial_driver_count=10,
        obstacles=obstacles,
        potholes=potholes,
        driver_weight=lambda: random.randint(1, 8),
        walker_weight=lambda: random.randint(1, 4),
        driver_maxspeed=lambda: random.randint(35, 55),
        walker_maxspeed=lambda: random.randint(3, 8),
        repopulate=True,
        steps=150,
        display=False,
    )

    result = run_simulation(config, include_heatmaps=True)
    print(f"Steps: {len(result.metrics)}, City shape: {result.city.city_grid.shape}")
    print(summarize_metrics(result))


if __name__ == "__main__":
    main()

