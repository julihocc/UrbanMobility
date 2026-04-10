from collections import defaultdict

import numpy as np

from utils.UrbanUtils import euclidean


class MetricsCollector:
    """Handles all per-step metric collection for a CityModel simulation."""

    def __init__(self, city, removal_times):
        self.city = city
        self.removal_times = removal_times
        h, w = city.city_grid.shape
        self.walker_speed_hm = np.zeros((h, w))
        self.driver_speed_hm = np.zeros((h, w))
        self.walker_count_hm = [[set() for _ in range(w)] for _ in range(h)]
        self.driver_count_hm = [[set() for _ in range(w)] for _ in range(h)]

    def collect(self, t, metrics):
        """Run all metric collection for time step t, writing into metrics[t]."""
        collisions = self._get_collisions()
        self._manage_collisions(collisions, t, metrics)
        self._manage_jaywalking(t, metrics)
        self._manage_active_agents(t, metrics)
        self._compute_average_speed(t, metrics)
        self._update_heatmaps()

    # ------------------------------------------------------------------

    def _get_collisions(self):
        city = self.city
        collisions = defaultdict(list)
        for agent in city.agents:
            for neigh in city.neighbors(agent, distance=1):
                if euclidean(agent.position, neigh.position) < (
                    agent.width + neigh.width
                ) / 2 and (
                    agent.agent_type == "driver" or neigh.agent_type == "driver"
                ):
                    pos = agent.grid_position()
                    pos = (int(pos[0]), int(pos[1]))
                    collisions[pos].extend([agent, neigh])
        return collisions

    def _manage_collisions(self, collisions, t, metrics):
        metrics[t]["collisions"] = []
        metrics[t]["runovers"] = []
        for key, agents in collisions.items():
            if any(a.active for a in agents):
                if all(a.agent_type == "driver" for a in agents):
                    metrics[t]["collisions"].append(key)
                else:
                    metrics[t]["runovers"].append(key)
            for agent in agents:
                if agent.active:
                    agent.deactivate(self.removal_times[type(agent)])

    def _manage_jaywalking(self, t, metrics):
        city = self.city
        jw = defaultdict(list)
        for agent in city.agents:
            pos = agent.grid_position()
            if (
                agent.agent_type == "walker"
                and pos in (set(city.road_cells) - set(city.zebras))
                and pos not in jw[agent.id]
            ):
                jw[agent.id].append(tuple(pos))
        metrics[t]["jaywalking"] = jw

    def _manage_active_agents(self, t, metrics):
        city = self.city
        walkers = [a for a in city.agents if a.agent_type == "walker"]
        drivers = [a for a in city.agents if a.agent_type == "driver"]
        parking = city.parking_cells()
        metrics[t]["env_walkers"] = len(walkers)
        metrics[t]["active_walkers"] = sum(1 for a in walkers if a.active)
        metrics[t]["env_drivers"] = len(drivers)
        metrics[t]["active_drivers"] = sum(1 for a in drivers if a.active)
        metrics[t]["parked_drivers"] = sum(
            1 for a in drivers if not a.active and a.grid_position() in parking
        )

    def _compute_average_speed(self, t, metrics):
        city = self.city
        walkers = [a for a in city.agents if a.agent_type == "walker"]
        drivers = [a for a in city.agents if a.agent_type == "driver"]
        metrics[t]["avg_speed_walkers"] = (
            float(np.mean([a.speed for a in walkers])) if walkers else 0.0
        )
        metrics[t]["avg_speed_drivers"] = (
            float(np.mean([a.speed for a in drivers])) if drivers else 0.0
        )

    def _update_heatmaps(self):
        city = self.city
        active_walkers = [
            a for a in city.agents if a.agent_type == "walker" and a.active
        ]
        active_drivers = [
            a for a in city.agents if a.agent_type == "driver" and a.active
        ]
        for w in active_walkers:
            pos = city.positions[w]
            self.walker_count_hm[pos[0]][pos[1]].add(w.id)
            n = len(self.walker_count_hm[pos[0]][pos[1]])
            self.walker_speed_hm[pos] = (
                (n - 1) * self.walker_speed_hm[pos] + w.speed
            ) / n
        for d in active_drivers:
            pos = city.positions[d]
            self.driver_count_hm[pos[0]][pos[1]].add(d.id)
            n = len(self.driver_count_hm[pos[0]][pos[1]])
            self.driver_speed_hm[pos] = (
                (n - 1) * self.driver_speed_hm[pos] + d.speed
            ) / n
