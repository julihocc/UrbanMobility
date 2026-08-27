"""SimulationResult serialization: serialize a run to dictionaries and JSON."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services import run_simulation_from_parameters
from utils.UrbanUtils import gen_city


def main():
    city_grid = gen_city(block_shape=(10, 10), city_shape=(2, 2), street_parking=False, crop=0)
    parameters = {
        'seed': 2,
        'city_grid': city_grid,
        'initial_walker_count': 8,
        'initial_driver_count': 6,
        'steps': 80,
        'display': False,
    }

    result = run_simulation_from_parameters(parameters, include_heatmaps=True)
    payload = result.to_dict(include_spawned_agents=False)
    print("Dict keys:", list(payload.keys()))

    json_text = result.to_json(include_spawned_agents=False, indent=2)
    print("JSON preview:")
    print(json_text[:700])


if __name__ == "__main__":
    main()

