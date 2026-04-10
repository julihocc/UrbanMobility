# %% [markdown]
# # SimulationResult Serialization
\n# This notebook shows how to serialize a run to dictionaries and JSON for reporting, APIs, or GUI integrations.\n\n# %%\nfrom pathlib import Path
\nimport sys
\n
\nROOT = Path.cwd()
\nif not (ROOT / 'services').exists():
\n    ROOT = ROOT.parent
\nif str(ROOT) not in sys.path:
\n    sys.path.insert(0, str(ROOT))\n\n# %%\nfrom services import run_simulation_from_parameters
\nfrom utils.UrbanUtils import gen_city
\n
\ncity_grid = gen_city(block_shape=(10, 10), city_shape=(2, 2), street_parking=False, crop=0)
\nparameters = {
\n    'seed': 2,
\n    'city_grid': city_grid,
\n    'initial_walker_count': 8,
\n    'initial_driver_count': 6,
\n    'steps': 80,
\n    'display': False,
\n}
\n
\nresult = run_simulation_from_parameters(parameters, include_heatmaps=True)
\npayload = result.to_dict(include_spawned_agents=False)
\npayload.keys()\n\n# %%\njson_text = result.to_json(include_spawned_agents=False, indent=2)
\njson_text[:700]\n\n