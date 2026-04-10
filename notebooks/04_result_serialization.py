# %% [markdown]
# # SimulationResult Serialization
# This notebook shows how to serialize a run to dictionaries and JSON for reporting, APIs, or GUI integrations.

# %%
from pathlib import Path
import sys

ROOT = Path.cwd()
if not (ROOT / 'services').exists():
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# %%
from services import run_simulation_from_parameters
from utils.UrbanUtils import gen_city

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
payload.keys()

# %%
json_text = result.to_json(include_spawned_agents=False, indent=2)
json_text[:700]

