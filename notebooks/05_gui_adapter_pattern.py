# %% [markdown]
# # GUI Adapter Pattern
# This notebook demonstrates how a GUI renderer can consume `SimulationController` without embedding simulation logic.

# %%
from pathlib import Path
import sys

ROOT = Path.cwd()
if not (ROOT / 'services').exists():
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# %%
from SimulationConfig import SimulationConfig
from gui import GuiRenderer, SimulationController
from utils.UrbanUtils import gen_city

class ConsoleRenderer(GuiRenderer):
    def render_simulation(self, result):
        print('Simulation completed')
        print('Steps:', len(result.metrics))
        print('City shape:', result.city.city_grid.shape)

    def render_error(self, message: str):
        print('Error:', message)

city_grid = gen_city(block_shape=(10, 10), city_shape=(1, 2), street_parking=False, crop=0)
config = SimulationConfig(
    seed=3,
    city_grid=city_grid,
    initial_walker_count=6,
    initial_driver_count=4,
    steps=50,
    display=False,
)

controller = SimulationController(ConsoleRenderer())
controller.run(config, include_heatmaps=False)
controller.last_result_json()[:300]

