from model.AgentImpl import *
from model.AgentSpawner import AgentSpawner
from model.MetricsCollector import MetricsCollector
from utils.UrbanUtils import *
import agentpy as ap, numpy as np


#######################################
# CLASS FOR THE SYSTEM (Ag, Env)
#######################################
class CityModel(ap.Model):
    def setup(self):
        self.p.city_grid = np.array(self.p.city_grid)
        self.city = City(self, shape=self.p.city_grid.shape)

        # Default removal times after incidents, maybe allow modifying from p.
        self.removal_times = {AstarDriver: 20, AstarWalker: 5}
        self.scheduled_removals = []
        # Initilize environment
        self.setup_grid_labels()
        self.metrics = {}
        # Agent history. Stores initialization data of each agent
        self.spawned_agents = {}
        self.repopulate = False if "repopulate" not in self.p else self.p.repopulate

        self.spawner = AgentSpawner(self, self.city)
        self.nwalkers, self.ndrivers = self.spawner.setup_initial_agents()
        self.spawned_agents = self.spawner.spawned_agents

        self.metrics_collector = MetricsCollector(self.city, self.removal_times)

        # Initializes labels and values for walker and driver agents.

    def setup_grid_labels(self):
        walk_terrain = [
            "s",
            "z",
            "p",
            "r",
            "t",
            "l",
            "b",
            "o",
        ]  # street, zcross, road, building, obstacle
        self.walk_cost = dict(zip(walk_terrain, [1, 1, 2, 5, 10, 20, 1000, 1000]))
        drive_terrain = ["s", "z", "p", "r", "t", "l", "b", "o", "ph"]
        self.drive_cost = dict(
            zip(drive_terrain, [1000, 2, 3, 1, 1, 1, 1000, 1001, 20])
        )
        drive_move = ["fw", "rt", "lt", "ch", "ft", "bw"]
        self.drive_risk = dict(zip(drive_move, [0, 1, 2, 10, 10, 15]))

    def update(self):
        # Update and collect metrics at time t
        self.metrics[self.t] = {}

        # Remove any agents scheduled for removal
        if self.scheduled_removals:
            self.city.remove_agents(self.scheduled_removals)
            self.scheduled_removals = []

        # Spawning walkers and drivers to match initial count
        if self.repopulate:
            active_walkers = sum(
                1 for a in self.city.agents if a.agent_type == "walker" and a.active
            )
            self.spawner.spawn_walkers(self.nwalkers - active_walkers)
            active_drivers = sum(
                1 for a in self.city.agents if a.agent_type == "driver" and a.active
            )
            self.spawner.spawn_drivers(self.ndrivers - active_drivers)

        # Manages goal reaching agents.
        self.goal_agents()

        # Sense-react-decide cycle.
        self.city.agents.sense()
        self.city.agents.react()
        self.city.agents.choose_action()

        # Monitoring metrics
        self.report_metrics()

    def goal_agents(self):
        arrivals = {}
        for agent in self.city.agents:
            if euclidean(agent.position, agent.goal) < 0.5:
                arrivals[agent.id] = self.t
                if agent.goal not in self.city.parking_spaces:
                    agent.deactivate(removal_time=0)
                else:
                    agent.deactivate(removal_time=np.inf)
        self.metrics[self.t]["arrivals"] = arrivals

    def step(self):
        # Compute every agent's next action
        self.city.agents.execute()
        # Stop execution when every agent is inactive and removed
        if len(self.city.agents) == 0 and "steps" not in self.p.keys():
            self.end()
            self.stop()

    def end(self):
        self.report("metrics", self.metrics)
        self.report("spawned_agents", self.spawned_agents)

    #####################################################################
    def report_metrics(self):
        self.metrics_collector.collect(self.t, self.metrics)

    # Agents scheduled for removal will be deleted from city next update
    def schedule_removal(self, agent):
        self.scheduled_removals.append(agent)


####################################################################
#####################################

#######################################
# CLASS FOR ENVIRONMENT
#######################################
"""
A grid of costs is generated for each agent type
"""


class City(ap.Grid):
    def setup(self):
        self.city_grid = self.p.city_grid
        grid, (h, w) = self.p.city_grid, self.p.city_grid.shape
        self.parking_spaces = (
            self.parking_cells()
        )  # Parking spaces are encoded in city_grid
        # Default attributes
        self.obstacles = set(self.p.obstacles) if "obstacles" in self.p else set([])
        self.potholes = set(self.p.potholes) if "potholes" in self.p else set([])
        self.driver_sources, self.driver_goals = (
            self.p.driver_endpoints
            if "driver_endpoints" in self.p
            else self.driver_endpoints()
        )
        self.walker_sources, self.walker_goals = (
            self.p.walker_endpoints
            if "driver_endpoints" in self.p
            else self.walker_endpoints()
        )
        self.road_cells = set(
            [
                tuple(x)
                for x in np.argwhere(
                    np.array(
                        [
                            grid[i, j][0] in ("r", "z", "p")
                            for i in range(h)
                            for j in range(w)
                        ]
                    ).reshape((h, w))
                )
            ]
        )
        self.zebras = set(
            [
                tuple(x)
                for x in np.argwhere(
                    np.array(
                        [grid[i, j][0] == "z" for i in range(h) for j in range(w)]
                    ).reshape((h, w))
                )
            ]
        )

    def is_intersection(self, cell):
        return not " " in self.city_grid[cell]

    def get_agents_at(self, position):
        return list(filter(lambda x: x.grid_position == position, self.agents))

    def walker_endpoints(self):
        # Pedestrians can be spawned from any sidewalk cell
        return get_walker_endpoints(self.city_grid)

    def parking_cells(self):
        return get_parking_spots(self.city_grid)

    def driver_endpoints(self):
        # Car will be spawned from street intersections on edges. These will also work as goals
        return get_driver_endpoints(self.city_grid)


# Backward compatibility for existing imports:
# from model.UrbanModelling import PoisonCityModel
from model.PoisonCityModel import PoisonCityModel  # noqa: E402
