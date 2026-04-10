import numpy as np

from model.UrbanModelling import CityModel


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
