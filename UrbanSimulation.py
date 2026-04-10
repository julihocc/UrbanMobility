# %% [markdown]
# # Pedestrians routes
\n# 
\n# This code snippet demonstrates a minimal agent-based simulation of pedestrian movement using weighted decision-making. Each pedestrian agent is characterized by two key parameters: risk weight and maximum speed. These parameters influence how agents choose paths and move through the environment.
\n# 
\n# **Walker Agent Parameters**: Agents can be initialized using exact coordinates (start and goal) to simulate specific situations. In this case, the *walkers* parameter contains specific data for each agent:
\n# - *Risk Weight:* The risk weight determines how strongly an agent prioritizes the shortest path over safer alternatives.
\n# - *Maximum Speed:* The maximum speed limits how far an agent can move per simulation step.
\n# - *Source and Destination (Start and Goal):* These parameters define the origin and target location of the driver within the road network and determine the general direction of travel.
\n# 
\n# **Behavioral Interpretation**: As expected, pedestrians with higher risk weights tend to prioritize efficiency, potentially increasing interactions with drivers. Walker agents with lower maximum speeds contribute to localized slowdowns and traffic accumulation. Different parameters values allow to observe heterogeneous microscopic behaviour.\n\n# %%\nfrom visual.AnimationUtils import animation_plot
\nfrom utils.UrbanUtils import gen_city, gen_obstacles
\nfrom notebooks_support import run_exploration, summarize_metrics
\nfrom matplotlib import pyplot as plt
\nimport agentpy as ap
\nimport IPython, random
\n
\nrandom.seed(0)
\nblock_shape, city_shape = (15, 12), (1, 2)
\ncity_grid = gen_city(block_shape, city_shape, street_parking=False, nlanes=2, crop=0)
\nobstacles, potholes = gen_obstacles(city_grid, 10, 10)
\n
\nparameters = {
\n    'city_grid': city_grid,
\n    'walkers': [{'start': (5, 9), 'goal':(9, 14), 'max_speed':5 + 2 * i, 'weight': i} for i in (1, 2, 3)],
\n    'steps': 60,
\n    'display': False
\n}
\nresult = run_exploration(parameters)
\nprint(summarize_metrics(result))
\nfig = plt.figure(figsize=(8, 4))
\nax = fig.add_subplot(111)
\nanimation = ap.animate(result.model, fig, ax, animation_plot)
\nIPython.display.HTML(animation.to_jshtml())\n\n# %% [markdown]
# # Drivers routes
\n# 
\n# This example simulates driver agents, whose behavior is also influenced by individual risk weights and speed constraints. As with pedestrians, these parameters introduce behavioral diversity and allow the simulation of different driving styles.
\n# 
\n# **Driver Agent Parameters:** Similar to walkers, each driver agent is initialized using the *drivers*, and including a set of attributes that define both its state and intended movement. An additional parameter allows drivers to have an initial direction.
\n# 
\n# **Behavioral Interpretation** During the simulation, drivers with higher risk weights tend to prioritize efficiency, potentially increasing interactions with pedestrians. Drivers with lower maximum speeds contribute to localized slowdowns and traffic accumulation.
\n# 
\n# Heterogeneous driver profiles result in emergent traffic patterns that would not appear in uniform-flow models.\n\n# %%\nfrom visual.AnimationUtils import animation_plot
\nfrom utils.UrbanUtils import gen_city, gen_obstacles
\nfrom model import CityModel
\nfrom matplotlib import pyplot as plt
\nimport agentpy as ap
\nimport IPython, random
\n
\nrandom.seed(0)
\nblock_shape, city_shape = (14, 16), (2, 3)
\ncity_grid = gen_city(block_shape, city_shape, street_parking=False, nlanes = 2, crop=0)
\ndrivers = [{'start': (9, 1), 'direction': (-1, 0), 'goal': (12, 5), 'max_speed': 60, 'weight': 1},
\n           {'start': (9, 17), 'direction': (-1, 0), 'goal': (12, 21), 'max_speed': 45, 'weight': 5},
\n           {'start': (9, 33), 'direction': (-1, 0), 'goal': (12, 37), 'max_speed': 30, 'weight': 10}
\n           ]
\n
\nparameters = {
\n    'seed': 0,
\n    'debug': False,
\n    'city_grid': city_grid,
\n    'walkers': [],
\n    'drivers': drivers,
\n    'steps': 40,
\n    'display': True
\n}
\nfig = plt.figure(figsize=(8, 6))
\nax = fig.add_subplot(111)
\nmodel = CityModel(parameters)
\nanimation = ap.animate(model, fig, ax, animation_plot)
\nIPython.display.HTML(animation.to_jshtml())\n\n# %% [markdown]
# # Reacting (drivers)
\n# 
\n# This simulation illustrates how driver agents interact in a reduced environment. At each step, agents sense their surroundings and react by modifying their speed, enabling the analysis of local traffic dynamics and interaction-driven slowdowns.
\n# 
\n# If direction is not assigned, a direction is automatically assigned according to street directions.\n\n# %%\nfrom visual.AnimationUtils import animation_plot
\nfrom utils.UrbanUtils import gen_city
\nfrom model import CityModel
\nfrom matplotlib import pyplot as plt
\nimport agentpy as ap
\nimport IPython
\n
\nblock_shape, city_shape = (15, 15), (2, 3)
\ncity_grid = gen_city(block_shape, city_shape, street_parking=False, two_way=True, crop=0)
\ndrivers = [{'start': (14, 11), 'goal': (1, 0), 'max_speed': 40},
\n           {'start': (23, 1), 'goal': (1, 0), 'max_speed': 35},
\n           {'start': (8, 14), 'goal': (29, 14), 'max_speed': 50},
\n           {'start': (22, 30), 'goal': (14, 0), 'max_speed': 60},
\n           {'start': (15, 6), 'goal': (29, 14), 'max_speed': 50},
\n           {'start': (15, 8), 'goal': (29, 14), 'max_speed': 40},
\n          ]
\n
\nparameters = {
\n    'debug': False,
\n    'city_grid': city_grid,
\n    'drivers': drivers,
\n    'steps': 50,
\n    'display': False
\n}
\nfig = plt.figure(figsize=(8, 6))
\nax = fig.add_subplot(111)
\nmodel = CityModel(parameters)
\nanimation = ap.animate(model, fig, ax, animation_plot)
\nIPython.display.HTML(animation.to_jshtml())\n\n# %% [markdown]
# ## Rerouting
\n# 
\n# Enabling agents to select alternative routes is useful to prevent deadlocks when preceding drivers remain stationary, improving overall traffic flow.\n\n# %%\nfrom visual.AnimationUtils import animation_plot
\nfrom utils.UrbanUtils import gen_city
\nfrom model import CityModel
\nfrom matplotlib import pyplot as plt
\nimport agentpy as ap
\nimport IPython
\n
\ncity_grid = gen_city(block_shape = (12, 15), city_shape=(2, 2), street_parking=False, nlanes=2, two_way=True, crop = 0)
\ndrivers = [#{'start': (4, 14), 'goal': (12, 29), 'max_speed': 60, 'weight': 1},
\n           {'start': (12, 15), 'goal': (0, 15), 'max_speed': 0, 'weight': 1},
\n           {'start': (19, 15), 'goal': (11, 0), 'max_speed': 60, 'weight': 1},
\n           {'start': (6, 14), 'goal': (12, 29), 'max_speed': 60, 'weight': 1}]
\nparameters = {
\n    'seed': 1,
\n    'debug': False,
\n    'city_grid': city_grid,
\n    'drivers': drivers,
\n    'obstacles': [(8, 12)],
\n    'steps': 50,
\n    'display': False
\n}
\n
\nfig = plt.figure(figsize=(8, 6))
\nax = fig.add_subplot(111)
\nmodel = CityModel(parameters)
\nanimation = ap.animate(model, fig, ax, animation_plot)
\nIPython.display.HTML(animation.to_jshtml())\n\n# %%\nfrom visual.AnimationUtils import animation_plot
\nfrom utils.UrbanUtils import gen_city
\nfrom model import CityModel
\nfrom matplotlib import pyplot as plt
\nimport agentpy as ap
\nimport IPython
\n
\ncity_grid = gen_city(block_shape = (12, 15), city_shape=(2, 2), street_parking=False, nlanes=2, two_way=True, crop = 0)
\ndrivers = [{'start': (19, 15), 'goal': (11, 0), 'max_speed': 60, 'weight': 1},
\n           {'start': (6, 14), 'goal': (12, 29), 'max_speed': 60, 'weight': 1},
\n           {'start': (11, 22), 'goal': (11, 0), 'max_speed': 60, 'weight': 1},
\n           {'start': (4, 14), 'goal': (12, 29), 'max_speed': 60, 'weight': 1},
\n           {'start': (23, 20), 'goal': (0, 15), 'max_speed': 60, 'weight': 1}
\n           ]
\nparameters = {
\n    'seed': 1,
\n    'debug': False,
\n    'city_grid': city_grid,
\n    'drivers': drivers,
\n    'obstacles': [(8, 12)],
\n    'steps': 50,
\n    'display': False
\n}
\n
\nfig = plt.figure(figsize=(8, 6))
\nax = fig.add_subplot(111)
\nmodel = CityModel(parameters)
\nanimation = ap.animate(model, fig, ax, animation_plot)
\nIPython.display.HTML(animation.to_jshtml())\n\n# %% [markdown]
# # Reacting, drivers and pedestrians
\n# 
\n# Next, a set of scenarios involving conflicts between drivers and pedestrians is presented, enabling the analysis of complex behaviors, incident occurrence, and emergency reactions.\n\n# %%\nfrom visual.AnimationUtils import animation_plot
\nfrom utils.UrbanUtils import gen_city
\nfrom model import CityModel
\nfrom matplotlib import pyplot as plt
\nimport agentpy as ap
\nimport IPython
\n
\ncity_grid = gen_city(block_shape = (12, 15), city_shape=(2, 2), street_parking=False, crop = 0)
\ndrivers = [{'start': (0, 7), 'goal': (13, 25), 'max_speed': 60, 'weight': 1}, {'start': (12, 7), 'goal': (12, 25), 'max_speed': 55, 'weight': 1}, {'start': (12, 0), 'goal': (12, 25), 'max_speed': 50, 'weight': 1}]
\nwalkers = [{'start': (6, 13), 'goal': (9, 13), 'max_speed': 7, 'weight': 1}, {'start': (13, 11), 'goal': (10, 10), 'max_speed': 10, 'weight': 1}]
\nparameters = {
\n    'seed': 0,
\n    'debug': False,
\n    'city_grid': city_grid,
\n    'walkers': walkers,
\n    'drivers': drivers,
\n    'obstacles': [(8, 13)],
\n    'steps': 40,
\n    'display': False,
\n}
\n
\nfig = plt.figure(figsize=(10, 6))
\nax = fig.add_subplot(111)
\nmodel = CityModel(parameters)
\nanimation = ap.animate(model, fig, ax, animation_plot)
\nIPython.display.HTML(animation.to_jshtml())\n\n# %% [markdown]
# # A complex and realistic simulation
\n# 
\n# Finally, a more complex simulation is presented to illustrate heterogeneous agent behavior in a more realistic urban scenario. The parameters *initial_driver_count* and *initial_walker_count* are used to initialize vehicles and pedestrians at random positions within the environment. In addition, the repopulate parameter enables the continuous generation of new agents, maintaining a stable population throughout the simulation.
\n# 
\n# Agent heterogeneity is introduced through additional parameters, namely *walker_weight*, *driver_weight*, *walker_maxspeed*, and *driver_maxspeed*. These parameters are defined as functions that return integer values, allowing variability in risk preference and mobility characteristics among agents.\n\n# %%\nfrom visual.AnimationUtils import animation_plot
\nfrom model import PoisonCityModel
\nfrom utils.UrbanUtils import gen_city, gen_obstacles
\nfrom matplotlib import pyplot as plt
\nimport agentpy as ap
\nimport IPython, random
\n
\nrandom.seed(0)
\ncity_grid = gen_city(block_shape = (15, 15), city_shape=(5, 5), street_parking=False, two_way=True, crop = 0)
\nobstacles, potholes = gen_obstacles(city_grid, obstacles=0.02, potholes=0)
\nparameters = {
\n    'seed': 0,
\n    'debug': False,
\n    'city_grid': city_grid,
\n    'initial_walker_count': 100,
\n    'initial_driver_count': 50,
\n    'obstacles': obstacles,
\n    'potholes': potholes,
\n    'driver_weight': lambda : random.randint(1, 10),
\n    'walker_weight': lambda : random.randint(1, 5),
\n    'driver_maxspeed': lambda : random.randint(40, 60),
\n    'walker_maxspeed': lambda : random.randint(4, 10),
\n    'repopulate': True,
\n    'steps': 120,
\n    'display': False
\n}
\n
\nfig = plt.figure(figsize=(8, 8))
\nax = fig.add_subplot(111)
\nmodel = PoisonCityModel(parameters)
\nanimation = ap.animate(model, fig, ax, animation_plot)
\nIPython.display.HTML(animation.to_jshtml())\n\n# %%\n\n