# %% [markdown]
# # Parameter Sweep Example
\n# This notebook runs several scenarios and compares collisions and runovers.\n\n# %%\nfrom pathlib import Path
\nimport sys
\n
\nROOT = Path.cwd()
\nif not (ROOT / 'services').exists():
\n    ROOT = ROOT.parent
\nif str(ROOT) not in sys.path:
\n    sys.path.insert(0, str(ROOT))\n\n# %%\nimport numpy as np
\n
\nfrom services import run_simulation_from_parameters
\nfrom notebooks_support import summarize_metrics
\nfrom utils.UrbanUtils import gen_city, gen_obstacles
\n
\ncity_grid = gen_city(block_shape=(14, 14), city_shape=(2, 2), street_parking=True, crop=2)
\nobstacle_shares = np.linspace(0.0, 0.1, 6)
\nrows = []
\n
\nfor share in obstacle_shares:
\n    parameters = {
\n        'seed': 0,
\n        'city_grid': city_grid,
\n        'initial_walker_count': 12,
\n        'initial_driver_count': 12,
\n        'obstacles': gen_obstacles(city_grid, obstacles=float(share))[0],
\n        'steps': 100,
\n        'display': False,
\n    }
\n    result = run_simulation_from_parameters(parameters)
\n    summary = summarize_metrics(result)
\n    summary['obstacle_share'] = float(share)
\n    rows.append(summary)
\n
\nrows\n\n