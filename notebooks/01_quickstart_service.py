# %% [markdown]
# # Quickstart: Run One Simulation Through the Service Layer
\n# This notebook shows the recommended path for running a simulation using the application service API.\n\n# %%\nfrom pathlib import Path
\nimport sys
\n
\nROOT = Path.cwd()
\nif not (ROOT / 'services').exists():
\n    ROOT = ROOT.parent
\nif str(ROOT) not in sys.path:
\n    sys.path.insert(0, str(ROOT))
\n
\nROOT\n\n# %%\nimport random
\n
\nfrom SimulationConfig import SimulationConfig
\nfrom services import run_simulation
\nfrom utils.UrbanUtils import gen_city, gen_obstacles
\n
\nseed = 7
\nrandom.seed(seed)
\ncity_grid = gen_city(block_shape=(12, 12), city_shape=(2, 2), street_parking=False, two_way=True, crop=0)
\nobstacles, potholes = gen_obstacles(city_grid, obstacles=0.01, potholes=0.01)
\n
\nconfig = SimulationConfig(
\n    seed=seed,
\n    city_grid=city_grid,
\n    initial_walker_count=20,
\n    initial_driver_count=10,
\n    obstacles=obstacles,
\n    potholes=potholes,
\n    driver_weight=lambda: random.randint(1, 8),
\n    walker_weight=lambda: random.randint(1, 4),
\n    driver_maxspeed=lambda: random.randint(35, 55),
\n    walker_maxspeed=lambda: random.randint(3, 8),
\n    repopulate=True,
\n    steps=150,
\n    display=False,
\n)
\n
\nresult = run_simulation(config, include_heatmaps=True)
\nlen(result.metrics), result.city.city_grid.shape\n\n# %%\nfrom notebooks_support import summarize_metrics
\n
\nsummarize_metrics(result)\n\n