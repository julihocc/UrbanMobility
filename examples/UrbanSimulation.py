"""Urban simulation: end-to-end walkthrough of pedestrian and driver scenarios.

This is a comprehensive, scenario-rich example that overlaps with the focused
examples in examples/01_... through examples/05_... .
Use the numbered examples for targeted workflows, and this one as an
end-to-end exploratory walkthrough.
"""

import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model import CityModel, PoisonCityModel
from examples_support import run_exploration, summarize_metrics
from utils.UrbanUtils import gen_city, gen_obstacles
from visual import AnimationRenderer, animation_plot

_ANIMATION_MODE = os.getenv("URBANMOBILITY_ANIMATION", "browser").strip().lower()
_ANIMATION_OUTPUT_DIR = ROOT / "images" / "animations"
_ANIMATION_RENDERER = AnimationRenderer(
    mode=_ANIMATION_MODE,
    output_dir=_ANIMATION_OUTPUT_DIR,
)


def _animate_model(model, scenario_name: str, figsize=(8, 6)):
    return _ANIMATION_RENDERER.animate_model(
        model,
        animation_plot,
        scenario_name,
        figsize=figsize,
    )


def scenario_pedestrian_routes():
    random.seed(0)
    city_grid = gen_city((15, 12), (1, 2), street_parking=False, nlanes=2, crop=0)
    gen_obstacles(city_grid, 10, 10)

    parameters = {
        "seed": 0,
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
    # Animate a fresh model instance to ensure frame-by-frame motion is rendered.
    _animate_model(CityModel(parameters), "pedestrian_routes", figsize=(8, 4))


def scenario_driver_routes():
    random.seed(0)
    city_grid = gen_city((14, 16), (2, 3), street_parking=False, nlanes=2, crop=0)
    drivers = [
        {"start": (9, 1), "direction": (-1, 0), "goal": (12, 5), "max_speed": 60, "weight": 1},
        {"start": (9, 17), "direction": (-1, 0), "goal": (12, 21), "max_speed": 45, "weight": 5},
        {"start": (9, 33), "direction": (-1, 0), "goal": (12, 37), "max_speed": 30, "weight": 10},
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
    _animate_model(CityModel(parameters), "driver_routes", figsize=(8, 6))


def scenario_reacting_drivers():
    city_grid = gen_city((15, 15), (2, 3), street_parking=False, two_way=True, crop=0)
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
    _animate_model(CityModel(parameters), "reacting_drivers", figsize=(8, 6))


def scenario_rerouting_blocked_driver():
    city_grid = gen_city(
        block_shape=(12, 15),
        city_shape=(2, 2),
        street_parking=False,
        nlanes=2,
        two_way=True,
        crop=0,
    )
    drivers = [
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
    _animate_model(CityModel(parameters), "rerouting_blocked_driver", figsize=(8, 6))


def scenario_rerouting_flow():
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
    _animate_model(CityModel(parameters), "rerouting_flow", figsize=(8, 6))


def scenario_reacting_mixed_agents():
    city_grid = gen_city((12, 15), (2, 2), street_parking=False, crop=0)
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
    _animate_model(CityModel(parameters), "reacting_mixed_agents", figsize=(10, 6))


def scenario_complex_realistic():
    random.seed(0)
    city_grid = gen_city((15, 15), (5, 5), street_parking=False, two_way=True, crop=0)
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
    _animate_model(PoisonCityModel(parameters), "complex_realistic", figsize=(8, 8))


def main():
    scenario_pedestrian_routes()
    scenario_driver_routes()
    scenario_reacting_drivers()
    scenario_rerouting_blocked_driver()
    scenario_rerouting_flow()
    scenario_reacting_mixed_agents()
    scenario_complex_realistic()
    _ANIMATION_RENDERER.finalize()


if __name__ == "__main__":
    main()

