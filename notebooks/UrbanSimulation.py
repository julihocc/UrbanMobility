# %% [markdown]
# # Pedestrians routes
#
# Note: This is a comprehensive, scenario-rich notebook that overlaps with the
# focused examples in `notebooks/01_...` through `notebooks/05_...`.
# Use the numbered notebooks for targeted workflows, and this one as an
# end-to-end exploratory walkthrough.
#
# This code snippet demonstrates a minimal agent-based simulation of pedestrian movement using weighted decision-making. Each pedestrian agent is characterized by two key parameters: risk weight and maximum speed. These parameters influence how agents choose paths and move through the environment.
#
# **Walker Agent Parameters**: Agents can be initialized using exact coordinates (start and goal) to simulate specific situations. In this case, the *walkers* parameter contains specific data for each agent:
# - *Risk Weight:* The risk weight determines how strongly an agent prioritizes the shortest path over safer alternatives.
# - *Maximum Speed:* The maximum speed limits how far an agent can move per simulation step.
# - *Source and Destination (Start and Goal):* These parameters define the origin and target location of the driver within the road network and determine the general direction of travel.
#
# **Behavioral Interpretation**: As expected, pedestrians with higher risk weights tend to prioritize efficiency, potentially increasing interactions with drivers. Walker agents with lower maximum speeds contribute to localized slowdowns and traffic accumulation. Different parameters values allow to observe heterogeneous microscopic behaviour.

# %%
from pathlib import Path
import sys
import os

# Support both script execution and interactive notebook execution.
if "__file__" in globals():
    ROOT = Path(__file__).resolve().parents[1]
else:
    ROOT = Path.cwd()
    if not (ROOT / "services").exists() and (ROOT.parent / "services").exists():
        ROOT = ROOT.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Use a non-interactive backend when running as a plain script.
os.environ.setdefault("MPLBACKEND", "Agg")


def render_animation(animation):
    try:
        from IPython import get_ipython
        import IPython.display as display

        if get_ipython() is not None:
            return display.HTML(animation.to_jshtml())
    except Exception:
        pass

    try:
        animation._draw_was_started = True
    except Exception:
        pass

    try:
        from matplotlib import pyplot as _plt

        _plt.close(animation._fig)
    except Exception:
        pass

    print(
        "Animation object created. Run this file as a notebook to display HTML animations."
    )
    return None


from visual.AnimationUtils import animation_plot
from utils.UrbanUtils import gen_city, gen_obstacles
from notebooks_support import run_exploration, summarize_metrics
from matplotlib import pyplot as plt
import agentpy as ap
import IPython, random

random.seed(0)
block_shape, city_shape = (15, 12), (1, 2)
city_grid = gen_city(block_shape, city_shape, street_parking=False, nlanes=2, crop=0)
obstacles, potholes = gen_obstacles(city_grid, 10, 10)

parameters = {
    "city_grid": city_grid,
    "walkers": [
        {"start": (5, 9), "goal": (9, 14), "max_speed": 5 + 2 * i, "weight": i}
        for i in (1, 2, 3)
    ],
    "steps": 60,
    "display": False,
}
result = run_exploration(parameters)
print(summarize_metrics(result))
fig = plt.figure(figsize=(8, 4))
ax = fig.add_subplot(111)
animation = ap.animate(result.model, fig, ax, animation_plot)
render_animation(animation)

# %% [markdown]
# # Drivers routes
#
# This example simulates driver agents, whose behavior is also influenced by individual risk weights and speed constraints. As with pedestrians, these parameters introduce behavioral diversity and allow the simulation of different driving styles.
#
# **Driver Agent Parameters:** Similar to walkers, each driver agent is initialized using the *drivers*, and including a set of attributes that define both its state and intended movement. An additional parameter allows drivers to have an initial direction.
#
# **Behavioral Interpretation** During the simulation, drivers with higher risk weights tend to prioritize efficiency, potentially increasing interactions with pedestrians. Drivers with lower maximum speeds contribute to localized slowdowns and traffic accumulation.
#
# Heterogeneous driver profiles result in emergent traffic patterns that would not appear in uniform-flow models.

# %%
from visual.AnimationUtils import animation_plot
from utils.UrbanUtils import gen_city, gen_obstacles
from model import CityModel
from matplotlib import pyplot as plt
import agentpy as ap
import IPython, random

random.seed(0)
block_shape, city_shape = (14, 16), (2, 3)
city_grid = gen_city(block_shape, city_shape, street_parking=False, nlanes=2, crop=0)
drivers = [
    {
        "start": (9, 1),
        "direction": (-1, 0),
        "goal": (12, 5),
        "max_speed": 60,
        "weight": 1,
    },
    {
        "start": (9, 17),
        "direction": (-1, 0),
        "goal": (12, 21),
        "max_speed": 45,
        "weight": 5,
    },
    {
        "start": (9, 33),
        "direction": (-1, 0),
        "goal": (12, 37),
        "max_speed": 30,
        "weight": 10,
    },
]

parameters = {
    "seed": 0,
    "debug": False,
    "city_grid": city_grid,
    "walkers": [],
    "drivers": drivers,
    "steps": 40,
    "display": True,
}
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111)
model = CityModel(parameters)
animation = ap.animate(model, fig, ax, animation_plot)
render_animation(animation)

# %% [markdown]
# # Reacting (drivers)
#
# This simulation illustrates how driver agents interact in a reduced environment. At each step, agents sense their surroundings and react by modifying their speed, enabling the analysis of local traffic dynamics and interaction-driven slowdowns.
#
# If direction is not assigned, a direction is automatically assigned according to street directions.

# %%
from visual.AnimationUtils import animation_plot
from utils.UrbanUtils import gen_city
from model import CityModel
from matplotlib import pyplot as plt
import agentpy as ap
import IPython

block_shape, city_shape = (15, 15), (2, 3)
city_grid = gen_city(
    block_shape, city_shape, street_parking=False, two_way=True, crop=0
)
drivers = [
    {"start": (14, 11), "goal": (1, 0), "max_speed": 40},
    {"start": (23, 1), "goal": (1, 0), "max_speed": 35},
    {"start": (8, 14), "goal": (29, 14), "max_speed": 50},
    {"start": (22, 30), "goal": (14, 0), "max_speed": 60},
    {"start": (15, 6), "goal": (29, 14), "max_speed": 50},
    {"start": (15, 8), "goal": (29, 14), "max_speed": 40},
]

parameters = {
    "debug": False,
    "city_grid": city_grid,
    "drivers": drivers,
    "steps": 50,
    "display": False,
}
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111)
model = CityModel(parameters)
animation = ap.animate(model, fig, ax, animation_plot)
render_animation(animation)

# %% [markdown]
# ## Rerouting
#
# Enabling agents to select alternative routes is useful to prevent deadlocks when preceding drivers remain stationary, improving overall traffic flow.

# %%
from visual.AnimationUtils import animation_plot
from utils.UrbanUtils import gen_city
from model import CityModel
from matplotlib import pyplot as plt
import agentpy as ap
import IPython

city_grid = gen_city(
    block_shape=(12, 15),
    city_shape=(2, 2),
    street_parking=False,
    nlanes=2,
    two_way=True,
    crop=0,
)
drivers = [  # {'start': (4, 14), 'goal': (12, 29), 'max_speed': 60, 'weight': 1},
    {"start": (12, 15), "goal": (0, 15), "max_speed": 0, "weight": 1},
    {"start": (19, 15), "goal": (11, 0), "max_speed": 60, "weight": 1},
    {"start": (6, 14), "goal": (12, 29), "max_speed": 60, "weight": 1},
]
parameters = {
    "seed": 1,
    "debug": False,
    "city_grid": city_grid,
    "drivers": drivers,
    "obstacles": [(8, 12)],
    "steps": 50,
    "display": False,
}

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111)
model = CityModel(parameters)
animation = ap.animate(model, fig, ax, animation_plot)
render_animation(animation)

# %%
from visual.AnimationUtils import animation_plot
from utils.UrbanUtils import gen_city
from model import CityModel
from matplotlib import pyplot as plt
import agentpy as ap
import IPython

city_grid = gen_city(
    block_shape=(12, 15),
    city_shape=(2, 2),
    street_parking=False,
    nlanes=2,
    two_way=True,
    crop=0,
)
drivers = [
    {"start": (19, 15), "goal": (11, 0), "max_speed": 60, "weight": 1},
    {"start": (6, 14), "goal": (12, 29), "max_speed": 60, "weight": 1},
    {"start": (11, 22), "goal": (11, 0), "max_speed": 60, "weight": 1},
    {"start": (4, 14), "goal": (12, 29), "max_speed": 60, "weight": 1},
    {"start": (23, 20), "goal": (0, 15), "max_speed": 60, "weight": 1},
]
parameters = {
    "seed": 1,
    "debug": False,
    "city_grid": city_grid,
    "drivers": drivers,
    "obstacles": [(8, 12)],
    "steps": 50,
    "display": False,
}

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111)
model = CityModel(parameters)
animation = ap.animate(model, fig, ax, animation_plot)
render_animation(animation)

# %% [markdown]
# # Reacting, drivers and pedestrians
#
# Next, a set of scenarios involving conflicts between drivers and pedestrians is presented, enabling the analysis of complex behaviors, incident occurrence, and emergency reactions.

# %%
from visual.AnimationUtils import animation_plot
from utils.UrbanUtils import gen_city
from model import CityModel
from matplotlib import pyplot as plt
import agentpy as ap
import IPython

city_grid = gen_city(
    block_shape=(12, 15), city_shape=(2, 2), street_parking=False, crop=0
)
drivers = [
    {"start": (0, 7), "goal": (13, 25), "max_speed": 60, "weight": 1},
    {"start": (12, 7), "goal": (12, 25), "max_speed": 55, "weight": 1},
    {"start": (12, 0), "goal": (12, 25), "max_speed": 50, "weight": 1},
]
walkers = [
    {"start": (6, 13), "goal": (9, 13), "max_speed": 7, "weight": 1},
    {"start": (13, 11), "goal": (10, 10), "max_speed": 10, "weight": 1},
]
parameters = {
    "seed": 0,
    "debug": False,
    "city_grid": city_grid,
    "walkers": walkers,
    "drivers": drivers,
    "obstacles": [(8, 13)],
    "steps": 40,
    "display": False,
}

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111)
model = CityModel(parameters)
animation = ap.animate(model, fig, ax, animation_plot)
render_animation(animation)

# %% [markdown]
# # A complex and realistic simulation
#
# Finally, a more complex simulation is presented to illustrate heterogeneous agent behavior in a more realistic urban scenario. The parameters *initial_driver_count* and *initial_walker_count* are used to initialize vehicles and pedestrians at random positions within the environment. In addition, the repopulate parameter enables the continuous generation of new agents, maintaining a stable population throughout the simulation.
#
# Agent heterogeneity is introduced through additional parameters, namely *walker_weight*, *driver_weight*, *walker_maxspeed*, and *driver_maxspeed*. These parameters are defined as functions that return integer values, allowing variability in risk preference and mobility characteristics among agents.

# %%
from visual.AnimationUtils import animation_plot
from model import PoisonCityModel
from utils.UrbanUtils import gen_city, gen_obstacles
from matplotlib import pyplot as plt
import agentpy as ap
import IPython, random

random.seed(0)
city_grid = gen_city(
    block_shape=(15, 15), city_shape=(5, 5), street_parking=False, two_way=True, crop=0
)
obstacles, potholes = gen_obstacles(city_grid, obstacles=0.02, potholes=0)
parameters = {
    "seed": 0,
    "debug": False,
    "city_grid": city_grid,
    "initial_walker_count": 100,
    "initial_driver_count": 50,
    "obstacles": obstacles,
    "potholes": potholes,
    "driver_weight": lambda: random.randint(1, 10),
    "walker_weight": lambda: random.randint(1, 5),
    "driver_maxspeed": lambda: random.randint(40, 60),
    "walker_maxspeed": lambda: random.randint(4, 10),
    "repopulate": True,
    "steps": 120,
    "display": False,
}

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111)
model = PoisonCityModel(parameters)
animation = ap.animate(model, fig, ax, animation_plot)
render_animation(animation)

# %%
