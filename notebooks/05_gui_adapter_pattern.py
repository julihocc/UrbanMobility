# %% [markdown]
# # GUI Adapter Pattern
\n# This notebook demonstrates how a GUI renderer can consume `SimulationController` without embedding simulation logic.\n\n# %%\nfrom pathlib import Path
\nimport sys
\n
\nROOT = Path.cwd()
\nif not (ROOT / 'services').exists():
\n    ROOT = ROOT.parent
\nif str(ROOT) not in sys.path:
\n    sys.path.insert(0, str(ROOT))\n\n# %%\nfrom SimulationConfig import SimulationConfig
\nfrom gui import GuiRenderer, SimulationController
\nfrom utils.UrbanUtils import gen_city
\n
\nclass ConsoleRenderer(GuiRenderer):
\n    def render_simulation(self, result):
\n        print('Simulation completed')
\n        print('Steps:', len(result.metrics))
\n        print('City shape:', result.city.city_grid.shape)
\n
\n    def render_error(self, message: str):
\n        print('Error:', message)
\n
\ncity_grid = gen_city(block_shape=(10, 10), city_shape=(1, 2), street_parking=False, crop=0)
\nconfig = SimulationConfig(
\n    seed=3,
\n    city_grid=city_grid,
\n    initial_walker_count=6,
\n    initial_driver_count=4,
\n    steps=50,
\n    display=False,
\n)
\n
\ncontroller = SimulationController(ConsoleRenderer())
\ncontroller.run(config, include_heatmaps=False)
\ncontroller.last_result_json()[:300]\n\n