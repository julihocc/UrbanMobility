# %% [markdown]
# # Heatmaps and Visualization Adapter
\n# This notebook demonstrates how to produce heatmaps from a service result and render them through visualization adapters.\n\n# %%\nfrom pathlib import Path
\nimport sys
\n
\nROOT = Path.cwd()
\nif not (ROOT / 'services').exists():
\n    ROOT = ROOT.parent
\nif str(ROOT) not in sys.path:
\n    sys.path.insert(0, str(ROOT))\n\n# %%\nimport random
\n
\nfrom SimulationConfig import SimulationConfig
\nfrom services import run_simulation
\nfrom utils.Reporting import generate_heatmaps
\nfrom utils.UrbanUtils import gen_city, gen_obstacles
\n
\nrandom.seed(1)
\ncity_grid = gen_city(block_shape=(15, 15), city_shape=(3, 3), street_parking=False, two_way=True, crop=0)
\nobstacles, potholes = gen_obstacles(city_grid, obstacles=0.02, potholes=0.01)
\n
\nconfig = SimulationConfig(
\n    seed=1,
\n    city_grid=city_grid,
\n    initial_walker_count=30,
\n    initial_driver_count=15,
\n    obstacles=obstacles,
\n    potholes=potholes,
\n    repopulate=True,
\n    steps=300,
\n    display=False,
\n)
\n
\nresult = run_simulation(config, include_heatmaps=True)
\nfig, axes = generate_heatmaps(result.city, result.heatmaps, figsize=(11, 8), show=True)
\nfig\n\n