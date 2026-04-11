"""Heatmaps and visualization: produce heatmaps from a service result."""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from SimulationConfig import SimulationConfig
from services import run_simulation
from utils.Reporting import generate_heatmaps
from utils.UrbanUtils import gen_city, gen_obstacles


def main():
    random.seed(1)
    city_grid = gen_city(block_shape=(15, 15), city_shape=(3, 3), street_parking=False, two_way=True, crop=0)
    obstacles, potholes = gen_obstacles(city_grid, obstacles=0.02, potholes=0.01)

    config = SimulationConfig(
        seed=1,
        city_grid=city_grid,
        initial_walker_count=30,
        initial_driver_count=15,
        obstacles=obstacles,
        potholes=potholes,
        repopulate=True,
        steps=300,
        display=False,
    )

    result = run_simulation(config, include_heatmaps=True)
    generate_heatmaps(result.city, result.heatmaps, figsize=(11, 8), show=True)


if __name__ == "__main__":
    main()

