---
description: "Use when editing code or notebooks in the UrbanMobility repository. Prefer preserving the simulation architecture, reproducibility, and analysis workflow."
name: "UrbanMobility Simulation Preferences"
applyTo: ["**/*.py", "**/*.ipynb"]
---
# UrbanMobility Simulation Preferences

These are best-practice preferences for this repository. Follow them unless a task explicitly requires a different approach.

- Prefer preserving the existing model layering: keep simulation orchestration in CityModel-like classes, shared agent behavior in base agent classes, and pathfinding or grid helpers in utility modules.
- Prefer extending the OODA-style agent loop through sense and react style methods rather than introducing one-off behavior flows.
- Prefer deterministic experiment setup for final or reporting runs: set or thread a seed in entry points and notebook executions when randomness is used.
- Prefer adding new simulation parameters in one place and keeping names consistent across main.py, Reporting.py, and notebook usage.
- Prefer metric-friendly changes: when behavior changes, keep or add observable outputs that can be compared across runs (for example heatmaps, counts, or speed/conflict summaries).
- Prefer notebook cells that are rerunnable from top to bottom without hidden state assumptions.
- Prefer small, focused edits that keep class and function naming consistent with existing PascalCase class names and snake_case methods/functions.

When these preferences conflict with explicit user instructions in a task, follow the explicit task instructions.
