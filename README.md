# Urban Mobility Simulation with Weighted A*

This repository contains a multi-agent urban mobility simulation for studying interactions between pedestrians and drivers on a grid-based city layout. The model combines weighted A* pathfinding, local sensing and reaction, and metric collection to analyze congestion, conflict zones, and mobility behavior under changing urban conditions.

The codebase is built around AgentPy and is currently organized as a research-style source tree, with the notebook serving as the clearest end-to-end walkthrough.

## Overview

The simulation models:

- Pedestrians and vehicles moving through the same city grid.
- Weighted A* routing that accounts for movement cost and behavioral risk.
- Local perception and reaction loops for agent decisions.
- Incident and movement metrics that can be aggregated into heatmaps.
- Experiment-style parameter variation for obstacle density and agent counts.

## Repository Layout

The main project code lives at the repository root:

- [UrbanSimulation.ipynb](./UrbanSimulation.ipynb): primary walkthrough for running and visualizing simulations.
- [main.py](./main.py): example seeded simulation setup for a single run.
- [Reporting.py](./Reporting.py): experiment-style script for parameter sweeps.
- [contracts/simulation_result.py](./contracts/simulation_result.py): result contract with JSON-friendly serialization.
- [services/simulation_service.py](./services/simulation_service.py): application service boundary for running simulations.
- [gui/controller.py](./gui/controller.py): GUI adapter skeleton that coordinates service calls and rendering.
- [notebooks_support/helpers.py](./notebooks_support/helpers.py): notebook-focused wrappers and metric summaries.
- [model/UrbanModelling.py](./model/UrbanModelling.py): `CityModel` orchestration, agent lifecycle, and metrics collection.
- [model/AgentBase.py](./model/AgentBase.py): base classes and shared agent behavior.
- [model/AgentImpl.py](./model/AgentImpl.py): concrete pedestrian and driver implementations.
- [utils/UrbanUtils.py](./utils/UrbanUtils.py): grid generation, obstacles, heuristics, and weighted A* utilities.
- [visual/AnimationUtils.py](./visual/AnimationUtils.py): visualization helpers.
- [images](./images): generated or referenced visual assets.

![UrbanMobility](./images/UrbanModel.gif)

## Environment Setup

Recommended baseline environment:

- Python 3.9 or newer
- `agentpy`
- `numpy`
- `matplotlib`
- `jupyter` for notebook-based exploration

Example setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install agentpy numpy matplotlib jupyter
```

## How to Use the Project

### Notebook-first workflow

Start with [UrbanSimulation.ipynb](./UrbanSimulation.ipynb). It is the best entrypoint for understanding:

- city generation
- agent initialization
- seeded simulation runs
- animation and visualization
- experiment iteration

This is the recommended path if you want a reproducible walkthrough of the model and its outputs.

Notebook exploration should call helpers from [notebooks_support/helpers.py](./notebooks_support/helpers.py):

- run_exploration(parameters, include_heatmaps=False) for executing simulation runs from notebook cells.
- summarize_metrics(result) for quick metric summaries without manually traversing nested dictionaries.

### Python scripts

The repository also includes script-based examples:

- [main.py](./main.py) shows how to configure a seeded city, run the application service, and produce heatmap-oriented outputs.
- [Reporting.py](./Reporting.py) shows how to build small experiment sweeps by varying parameters across multiple runs through the service layer.

These files are useful references when moving notebook logic into reusable Python code.

### Application service API

Use [services/simulation_service.py](./services/simulation_service.py) as the execution boundary between domain logic and interfaces:

- run_simulation(config, model_cls=CityModel, include_heatmaps=False)
- run_simulation_from_parameters(parameters, model_cls=CityModel, include_heatmaps=False)

Both functions return [contracts/simulation_result.py](./contracts/simulation_result.py) SimulationResult objects.

### Result contract and serialization

[contracts/simulation_result.py](./contracts/simulation_result.py) provides a transport-friendly output object for scripts, notebook cells, and GUI controllers.

- to_dict(include_metrics=True, include_spawned_agents=True, include_heatmaps=True)
- to_json(include_metrics=True, include_spawned_agents=True, include_heatmaps=True, indent=2)

The serializer normalizes nested values to builtin JSON-friendly structures to simplify persistence and external integration.

### GUI adapter boundary

[gui/controller.py](./gui/controller.py) and [gui/renderers.py](./gui/renderers.py) provide a minimal adapter interface for frontends:

- SimulationController executes runs and stores last_result.
- GuiRenderer defines rendering contracts for successful runs and errors.

This keeps GUI concerns outside domain and application layers.

## Model Concepts

Key implementation ideas in the current codebase:

- `CityModel` manages environment setup, spawning, simulation steps, and reporting.
- Agents follow a sense-react-choose-execute cycle.
- Weighted A* is used to generate routes through a city encoding that distinguishes roads, sidewalks, crossings, turns, parking, buildings, obstacles, and potholes.
- Metrics include arrivals, collisions, jaywalking-related behavior, average speed, and spatial heatmaps.

## Reproducibility Notes

The project already uses seeded randomness in its main simulation entrypoint. For comparable experiments and reporting runs, keep seeds explicit and keep parameter names aligned across notebooks and scripts.

## Current State

This repository is best treated as a simulation and analysis workspace rather than a packaged Python library. The notebook and source files document the intended workflow, while scripts serve as concrete examples for extending experiments and analysis.

## Separation of Concerns

The codebase now follows a lightweight layered structure:

- Domain logic: `model/` contains simulation rules and state transitions.
- Application services: `services/` provides run use-cases for scripts, GUI, and notebooks.
- Contracts: `contracts/` defines result objects and serialization boundaries.
- Adapters: `visual/`, `gui/`, and `notebooks_support/` consume service outputs for different user interfaces.

Recommended dependency direction:

- model -> no dependency on services, gui, notebooks_support.
- services -> depends on model and contracts.
- adapters (visual, gui, notebooks_support) -> depend on services and contracts.
- entrypoints (main, Reporting, notebooks) -> depend on adapters and services, not directly on low-level model internals unless required for experimentation.

## Migration Checklist

Use this checklist when updating legacy scripts or notebook cells.

### 1) Replace direct model execution

Before:

```python
from model.UrbanModelling import CityModel

model = CityModel(parameters)
model.run()
```

After:

```python
from services import run_simulation_from_parameters

result = run_simulation_from_parameters(parameters)
```

### 2) Replace notebook cell orchestration

Before:

```python
from model import CityModel

model = CityModel(parameters)
model.run()
```

After:

```python
from notebooks_support import run_exploration, summarize_metrics

result = run_exploration(parameters)
print(summarize_metrics(result))
```

### 3) Keep visualization as an adapter

- Continue using [visual/AnimationUtils.py](./visual/AnimationUtils.py) for rendering only.
- Pass service results to visual routines, for example `result.model` or `result.heatmaps`.
- Avoid placing simulation rules in plotting functions.

### 4) Use SimulationResult for data exchange

- Use `result.metrics`, `result.spawned_agents`, and `result.heatmaps` from [contracts/simulation_result.py](./contracts/simulation_result.py).
- Use `result.to_dict()` or `result.to_json()` when exporting results to files, APIs, or GUI layers.

### 5) Migrate script entrypoints

- Keep configuration in [SimulationConfig.py](./SimulationConfig.py).
- Use `run_simulation(config, include_heatmaps=...)` in [main.py](./main.py)-style workflows.
- Use `run_simulation_from_parameters(parameters)` in [Reporting.py](./Reporting.py)-style sweeps.

### 6) Migrate GUI integrations

- Use [gui/controller.py](./gui/controller.py) as the frontend entrypoint.
- Implement a [gui/renderers.py](./gui/renderers.py) `GuiRenderer` for your framework (Qt, Tkinter, web bridge, etc.).
- Keep GUI framework code out of domain and services layers.

### 7) Verify migration safety

- Run a fixed-seed scenario before and after migration.
- Compare key outputs: arrivals, collisions, runovers, and heatmaps.
- Keep parameter names and defaults aligned between scripts and notebooks.
