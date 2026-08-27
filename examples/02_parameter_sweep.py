"""Parameter sweep: run several scenarios and compare collisions and runovers."""
import pprint
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples_support import summarize_metrics
from services import run_simulation_from_parameters
from utils.UrbanUtils import gen_city, gen_obstacles


def main():
    city_grid = gen_city(block_shape=(14, 14), city_shape=(2, 2), street_parking=True, crop=2)
    obstacle_shares = np.linspace(0.0, 0.1, 6)
    rows = []

    for share in obstacle_shares:
        parameters = {
            'seed': 0,
            'city_grid': city_grid,
            'initial_walker_count': 12,
            'initial_driver_count': 12,
            'obstacles': gen_obstacles(city_grid, obstacles=float(share))[0],
            'steps': 100,
            'display': False,
        }
        result = run_simulation_from_parameters(parameters)
        summary = summarize_metrics(result)
        summary['obstacle_share'] = float(share)
        rows.append(summary)

    pprint.pprint(rows)


if __name__ == "__main__":
    main()


