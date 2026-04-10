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
def animation_plot(model, ax):
    plot_city(model.city, ax, alpha="80")
    plot_agents(model.city, ax)
    plot_collisions(model.metrics, ax)
    """
    for t in range(max(0, model.t - 10), model.t):
        if 'collisions' in model.metrics[t].keys():
            for collision in model.metrics[t]['collisions']:
                ax.text(collision[1] - 1.25, collision[0], "\u2739", fontsize=30, color='red')
        if 'runovers' in model.metrics[t].keys():
            for runover in model.metrics[t]['runovers']:
                ax.text(runover[1] - 1.25, runover[0], "\u2739", fontsize=30, color='red')

    ncollisions = sum([len(model.metrics[t]['collisions']) for t in range(0, model.t)])
    nrunovers = sum([len(model.metrics[t]['runovers']) for t in range(0, model.t)])
    ax.set_title('t: {}, runovers: {}, collisions: {}'.format(model.t, nrunovers, ncollisions))"""


def plot_collisions(metrics, ax):
    T = max(metrics.keys())
    for t in range(max(0, T - 10), T):
        if "collisions" in metrics[t].keys():
            for collision in metrics[t]["collisions"]:
                ax.text(
                    collision[1] - 1.25,
                    collision[0],
                    "\u2739",
                    fontsize=30,
                    color="red",
                )
        if "runovers" in metrics[t].keys():
            for runover in metrics[t]["runovers"]:
                ax.text(
                    runover[1] - 1.25, runover[0], "\u2739", fontsize=30, color="red"
                )

    ncollisions = sum([len(metrics[t]["collisions"]) for t in range(0, T)])
    nrunovers = sum([len(metrics[t]["runovers"]) for t in range(0, T)])
    ax.set_title(
        "t: {}, runovers: {}, collisions: {}".format(T, nrunovers, ncollisions)
    )


def plot_agents(city, ax):
    agents = city.agents
    fig_w, fig_h = ax.figure.get_size_inches()
    h, w = city.city_grid.shape
    marker_dict = {
        (-1, 0): "^",
        (1, 0): "v",
        (0, 1): ">",
        (0, -1): "<",
        (0, 0): "o",
    }  # Directions of agents
    for agent in agents:
        pos, dir = agent.position, agent.direction
        (color, size) = (
            ("black", 30)
            if agent.agent_type == "walker"
            else ("blue", 60)
            if agent.active
            else ("white", 60)
        )
        msize = 0.9 * size * fig_w / w
        ax.plot(
            pos[1] - 0.5, pos[0] - 0.5, marker_dict[dir], markersize=msize, color=color
        )  # Agent plot

        # Plotting future positions
        n = len(agent.next_real)
        for i in range(n):
            np = agent.next_real[i]
            ax.plot(
                [np[1] - 0.5],
                [np[0] - 0.5],
                marker="o",
                color=color,
                markersize=msize / 6,
                alpha=(n - i) / n,
            )


def plot_city(city, ax, alpha="ff"):
    city_grid, obstacles, potholes = city.city_grid, city.obstacles, city.potholes

    h, w = city_grid.shape
    st, gl, b, o, p, r, s, z, ph = -1, -2, 1000, 100, 9, 10, 1, 2, 5
    values = dict(zip(["b", "p", "r", "t", "l", "s", "z"], [b, p, r, r, r, s, z]))
    grid = np.array(
        [values[city_grid[i, j][0]] for i in range(h) for j in range(w)]
    ).reshape((h, w))

    for obst in obstacles:
        ax.plot(
            [obst[1]],
            [obst[0]],
            "H",
            markersize=6,
            markerfacecolor="#636363",
            markeredgecolor="r",
            markeredgewidth=1,
        )

    for pth in potholes:
        ax.plot(
            [pth[1]],
            [pth[0]],
            "s",
            markersize=4,
            markerfacecolor="#795c34",
            markeredgecolor="#795c34",
            markeredgewidth=1,
        )

    parking_cells = [
        tuple(x)
        for x in np.argwhere(
            np.array(
                [city_grid[i, j][0] == "p" for i in range(h) for j in range(w)]
            ).reshape((h, w))
        )
    ]
    poffset = 1 if parking_cells else 0
    for pc in parking_cells:
        ax.text(
            pc[1] - 0.25,
            pc[0] + 0.25,
            "P",
            color="white",
            fontsize=10,
            fontweight="bold",
        )
        # ax.plot([pc[1]], [pc[0]], 's', markersize=4, markerfacecolor='#795c34', markeredgecolor='#795c34',markeredgewidth=1)

    # Plotting turns
    rt_cells = [
        tuple(x)
        for x in np.argwhere(
            np.array(
                [city_grid[i, j][0] == "t" for i in range(h) for j in range(w)]
            ).reshape((h, w))
        )
    ]
    ar_offset1 = 2.5 + poffset
    ar_offset2 = 2.25 + poffset
    for cell in rt_cells:
        if city_grid[cell][1:] == "NE":
            if cell[0] > 0:
                if city_grid[cell[0] - 1, cell[1]][1:] == "NE":
                    ax.arrow(
                        cell[1] - 1,
                        cell[0] + ar_offset1,
                        0,
                        -0.5,
                        width=0.15,
                        head_width=0.3,
                        head_length=0.25,
                        fc="white",
                        ec="white",
                    )
                else:
                    ax.arrow(
                        cell[1] - 1,
                        cell[0] + ar_offset1 - 0.75,
                        0,
                        0.5,
                        width=0.15,
                        head_width=0.3,
                        head_length=0.25,
                        fc="white",
                        ec="white",
                    )
            ax.arrow(
                cell[1],
                cell[0] + ar_offset1,
                0,
                -0.5,
                width=0.15,
                head_width=0.3,
                head_length=0.25,
                fc="white",
                ec="white",
            )
            ax.arrow(
                cell[1],
                cell[0] + ar_offset2,
                0.25,
                0,
                width=0.15,
                head_width=0.3,
                head_length=0.25,
                fc="white",
                ec="white",
            )
        if city_grid[cell][1:] == "NW":
            if cell[1] < w - 1:
                if city_grid[cell[0], cell[1] + 1][1:] == "NW":
                    ax.arrow(
                        cell[1] + ar_offset1,
                        cell[0] + 1,
                        -0.5,
                        0,
                        width=0.15,
                        head_width=0.3,
                        head_length=0.25,
                        fc="white",
                        ec="white",
                    )
                else:
                    ax.arrow(
                        cell[1] + ar_offset1 - 0.75,
                        cell[0] + 1,
                        0.5,
                        0,
                        width=0.15,
                        head_width=0.3,
                        head_length=0.25,
                        fc="white",
                        ec="white",
                    )
            ax.arrow(
                cell[1] + ar_offset1,
                cell[0],
                -0.5,
                0,
                width=0.15,
                head_width=0.3,
                head_length=0.25,
                fc="white",
                ec="white",
            )
            ax.arrow(
                cell[1] + ar_offset2,
                cell[0],
                0,
                -0.25,
                width=0.15,
                head_width=0.3,
                head_length=0.25,
                fc="white",
                ec="white",
            )
        if city_grid[cell][1:] == "SE":
            if cell[1] > 0:
                if city_grid[cell[0], cell[1] - 1][1:] == "SE":
                    ax.arrow(
                        cell[1] - ar_offset1,
                        cell[0] - 1,
                        0.5,
                        0,
                        width=0.15,
                        head_width=0.3,
                        head_length=0.25,
                        fc="white",
                        ec="white",
                    )
                else:
                    ax.arrow(
                        cell[1] - ar_offset1 + 0.75,
                        cell[0] - 1,
                        -0.5,
                        0,
                        width=0.15,
                        head_width=0.3,
                        head_length=0.25,
                        fc="white",
                        ec="white",
                    )
            ax.arrow(
                cell[1] - ar_offset1,
                cell[0],
                0.5,
                0,
                width=0.15,
                head_width=0.3,
                head_length=0.25,
                fc="white",
                ec="white",
            )
            ax.arrow(
                cell[1] - ar_offset2,
                cell[0],
                0,
                0.25,
                width=0.15,
                head_width=0.3,
                head_length=0.25,
                fc="white",
                ec="white",
            )
        if city_grid[cell][1:] == "SW":
            if cell[0] < h - 1:
                if city_grid[cell[0] + 1, cell[1]][1:] == "SE":
                    ax.arrow(
                        cell[1] + 1,
                        cell[0] - ar_offset1,
                        0,
                        0.5,
                        width=0.15,
                        head_width=0.3,
                        head_length=0.25,
                        fc="white",
                        ec="white",
                    )
                else:
                    ax.arrow(
                        cell[1] + 1,
                        cell[0] - ar_offset1 + 0.75,
                        0,
                        -0.5,
                        width=0.15,
                        head_width=0.3,
                        head_length=0.25,
                        fc="white",
                        ec="white",
                    )
            ax.arrow(
                cell[1],
                cell[0] - ar_offset1,
                0,
                0.5,
                width=0.15,
                head_width=0.3,
                head_length=0.25,
                fc="white",
                ec="white",
            )
            ax.arrow(
                cell[1],
                cell[0] - ar_offset2,
                -0.25,
                0,
                width=0.15,
                head_width=0.3,
                head_length=0.25,
                fc="white",
                ec="white",
            )

    ax.set_xlim(-0.5, w - 0.5)
    ax.set_ylim(h - 0.5, -0.5)
    # Colors: black = edge, white = floor, green = goal, blue = agent
    # color_dict = {s: '#63636380', z: '#ffde2180', b: '#aa4a4480', r:'#82828280', o:'#ff000080', p:'#57a0d280'}
    color_dict = {
        s: "#AAAAAA" + alpha,
        z: "#FFFFFF" + alpha,
        b: "#708238" + alpha,
        r: "#333333" + alpha,
        p: "#57a0d2" + alpha,
    }

    ap.gridplot(grid, ax=ax, color_dict=color_dict, convert=True)


####################################################################


#####################################################################


#######################################
# CLASS FOR RANDOM AGENT GENERATION -- FOR SIMULATION PURPOSES
#######################################
class PoisonCityModel(CityModel):
    def update(self):
        # Update and collect metrics at time t
        self.metrics[self.t] = {}

        # Remove any agents scheduled for removal
        if self.scheduled_removals:
            self.city.remove_agents(self.scheduled_removals)
            self.scheduled_removals = []

        # Spawning walkers and drivers per step
        cur_nwalkers = len(
            list(filter(lambda x: x.agent_type == "walker", self.city.agents))
        )
        cur_ndrivers = len(
            list(filter(lambda x: x.agent_type == "driver", self.city.agents))
        )
        N = self.p.initial_walker_count - cur_nwalkers
        n = 0 if N < 0 else max(0, np.random.poisson(N))
        self.spawner.spawn_walkers(n)
        N = self.p.initial_driver_count - cur_ndrivers
        n = 0 if N < 0 else max(0, np.random.poisson(N))
        self.spawner.spawn_drivers(n)

        # Manages goal reaching agents.
        self.goal_agents()

        # Sense-react-decide cycle.
        self.city.agents.sense()
        self.city.agents.react()
        self.city.agents.choose_action()

        # Monitoring metrics
        self.report_metrics()

        # Verifies if every driver has stopped and finish simulation
        # if self.metrics[self.t]['avg_speed_drivers'] < 1:
        #     from matplotlib import pyplot as plt
        #     fig = plt.figure(figsize=(10, 10))
        #     ax = fig.add_subplot(111)
        #     animation_plot(self, ax)
        #     plt.show()
        #     self.stop()


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
