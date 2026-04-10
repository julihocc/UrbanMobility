import random

from SimulationConfig import SimulationConfig
from model.UrbanModelling import CityModel
from utils.Reporting import load_heatmaps, generate_heatmaps
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

    model = CityModel(config.to_parameters())
    model.run()
    heatmaps = load_heatmaps(model)
    generate_heatmaps(model.city, heatmaps, figsize=(12, 10))


if __name__ == "__main__":
    main()
