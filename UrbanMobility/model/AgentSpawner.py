from model.AgentImpl import AstarDriver, AstarWalker
from model.AgentBase import MobileAgent
from utils.UrbanUtils import manhattan


class AgentSpawner:
    """Handles all agent creation and registration for a CityModel simulation.

    Owns the spawned_agents registry and the per-agent-type weight/speed
    factories. CityModel delegates all spawn calls here and reads back
    nwalkers/ndrivers after initial setup.
    """

    WALKER_DEFAULTS = {
        "max_speed": 10,
        "visibility": 3,
        "awareness": 1,
        "weight": 1,
    }
    DRIVER_DEFAULTS = {
        "max_speed": 60,
        "visibility": 5,
        "awareness": 1,
        "weight": 1,
    }

    def __init__(self, model, city):
        self.model = model
        self.city = city
        self.spawned_agents: dict = {}

        p = model.p
        self.walker_weight = p.walker_weight if "walker_weight" in p else lambda: 1
        self.driver_weight = p.driver_weight if "driver_weight" in p else lambda: 1
        self.walker_maxspeed = (
            p.walker_maxspeed if "walker_maxspeed" in p else lambda: 10
        )
        self.driver_maxspeed = (
            p.driver_maxspeed
            if "driver_maxspeed" in p
            else lambda: MobileAgent.SPEED_LIMIT
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def setup_initial_agents(self) -> tuple[int, int]:
        """Spawn the initial walker and driver populations.

        Returns (nwalkers, ndrivers) so CityModel can track the target counts.
        """
        nwalkers = self._setup_walkers()
        ndrivers = self._setup_drivers()
        return nwalkers, ndrivers

    def spawn_walkers(self, n: int) -> None:
        """Spawn n random walkers from available sidewalk sources."""
        city, model, rnd = self.city, self.model, self.model.random
        agents, pos = [], []
        for _ in range(n):
            start = list(rnd.choice(city.walker_sources))
            position = (
                start[0] + rnd.uniform(0.1, 0.9),
                start[1] + rnd.uniform(0.1, 0.9),
            )
            goal = rnd.choice(city.walker_goals)
            direction = rnd.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            agent = AstarWalker(
                model,
                position,
                goal,
                direction=direction,
                speed=self.walker_maxspeed(),
                weight=self.walker_weight(),
            )
            pos.append(start)
            agents.append(agent)
        city.add_agents(agents, positions=pos)
        for agent in agents:
            agent.find_route()
            agent.initialize_agent()
            self._register(agent)

    def spawn_drivers(self, n: int, sources=None) -> None:
        """Spawn n random drivers from available road edge sources."""
        city, model, rnd = self.city, self.model, self.model.random
        sources = city.driver_sources[:] if sources is None else list(sources)
        sources = list(set(sources).difference(city.positions.values()))
        agents, pos = [], []
        for _ in range(n):
            start = rnd.choice(sources)
            goal = rnd.choice(city.driver_goals)
            while manhattan(goal, start) < 10:
                goal = rnd.choice(city.driver_goals)
            position = (start[0] + 0.5, start[1] + 0.5)
            ways = city.city_grid[start][1:].strip()
            direction = (
                MobileAgent.ACTION_MAP[rnd.choice("NSEW")]
                if ways == ""
                else MobileAgent.ACTION_MAP[rnd.choice(ways)]
            )
            agent = AstarDriver(
                model,
                position,
                goal,
                direction=direction,
                speed=self.driver_maxspeed(),
                weight=self.driver_weight(),
            )
            agents.append(agent)
            pos.append(start)
            sources.remove(start)
        city.add_agents(agents, positions=pos)
        for agent in agents:
            agent.find_route()
            agent.initialize_agent()
            self._register(agent)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _register(self, agent) -> None:
        self.spawned_agents[agent.id] = {
            "start": agent.start,
            "goal": agent.goal,
            "type": agent.agent_type,
            "spawn_time": self.model.t,
            "max_speed": agent.max_speed,
        }

    def _setup_walkers(self) -> int:
        p = self.model.p
        if "walkers" not in p:
            n = p.initial_walker_count if "initial_walker_count" in p else 0
            self.spawn_walkers(n)
            return n

        agents = []
        rnd = self.model.random
        for walker in p.walkers:
            d = walker.get("direction", rnd.choice([(0, 1), (0, -1), (1, 0), (-1, 0)]))
            s = walker.get("max_speed", self.WALKER_DEFAULTS["max_speed"])
            v = walker.get("visibility", self.WALKER_DEFAULTS["visibility"])
            w = walker.get("weight", self.WALKER_DEFAULTS["weight"])
            a = walker.get("awareness", self.WALKER_DEFAULTS["awareness"])
            start = walker["start"]
            position = tuple(start[i] + rnd.uniform(0.1, 0.9) for i in (0, 1))
            agent = AstarWalker(
                self.model,
                position,
                walker["goal"],
                direction=d,
                speed=s,
                visibility=v,
                awareness=a,
                weight=w,
            )
            agents.append(agent)
            self.city.add_agents([agent], positions=[start])
            agent.find_route()
            self._register(agent)
        for agent in agents:
            agent.initialize_agent()
        return len(agents)

    def _setup_drivers(self) -> int:
        p = self.model.p
        if "drivers" not in p:
            n = p.initial_driver_count if "initial_driver_count" in p else 0
            self.spawn_drivers(n, sources=self.city.road_cells)
            return n

        agents = []
        rnd = self.model.random
        for driver in p.drivers:
            s = driver.get("max_speed", self.DRIVER_DEFAULTS["max_speed"])
            v = driver.get("visibility", self.DRIVER_DEFAULTS["visibility"])
            w = driver.get("weight", self.DRIVER_DEFAULTS["weight"])
            a = driver.get("awareness", self.DRIVER_DEFAULTS["awareness"])
            start = driver["start"]
            if "direction" not in driver:
                ways = self.city.city_grid[start][1:].strip()
                direction = (
                    MobileAgent.ACTION_MAP[rnd.choice("NSEW")]
                    if ways == ""
                    else MobileAgent.ACTION_MAP[rnd.choice(ways)]
                )
            else:
                direction = driver["direction"]
            position = tuple(start[i] + rnd.uniform(0.4, 0.6) for i in (0, 1))
            agent = AstarDriver(
                self.model,
                position,
                driver["goal"],
                direction=direction,
                speed=s,
                visibility=v,
                awareness=a,
                weight=w,
            )
            agents.append(agent)
            self.city.add_agents([agent], positions=[start])
            agent.find_route()
            self._register(agent)
        for agent in agents:
            agent.initialize_agent()
        return len(agents)
