import random

from SimulationConfig import SimulationConfig
from services.simulation_service import run_simulation
from utils.Reporting import generate_heatmaps
from utils.UrbanUtils import gen_city, gen_obstacles


def main():
    seed = 0
    random.seed(seed)
    city_grid = gen_city(
        block_shape=(15, 15),
        city_shape=(5, 5),
        street_parking=False,
        two_way=True,
        crop=0,
    )
    obstacles, potholes = gen_obstacles(city_grid, obstacles=0.02, potholes=0.02)
    config = SimulationConfig(
        seed=seed,
        debug=False,
        city_grid=city_grid,
        initial_walker_count=100,
        initial_driver_count=50,
        obstacles=obstacles,
        potholes=potholes,
        driver_weight=lambda: random.randint(1, 10),
        walker_weight=lambda: random.randint(1, 5),
        driver_maxspeed=lambda: random.randint(40, 60),
        walker_maxspeed=lambda: random.randint(4, 10),
        repopulate=True,
        steps=10000,
        display=False,
    )

    result = run_simulation(config, include_heatmaps=True)
    generate_heatmaps(result.city, result.heatmaps, figsize=(12, 10))


if __name__ == "__main__":
    main()
