from SimulationConfig import SimulationConfig
from model.UrbanModelling import CityModel
import numpy as np

from utils.UrbanUtils import gen_city, gen_obstacles


def build_parameter_sweep():
    city_grid = gen_city(
        block_shape=(15, 15), city_shape=(3, 3), street_parking=True, crop=4
    )
    return [
        SimulationConfig(
            seed=0,
            debug=False,
            city_grid=city_grid,
            initial_walker_count=10,
            initial_driver_count=10,
            obstacles=gen_obstacles(city_grid, obstacles=obstacle_share)[0],
            max_walker_spawn=1,
            max_driver_spawn=1,
            steps=50,
            display=False,
        ).to_parameters()
        for obstacle_share in np.linspace(0, 0.2, 11)
    ]


def main():
    for parameters in build_parameter_sweep():
        model = CityModel(parameters)
        model.run()


if __name__ == "__main__":
    main()
