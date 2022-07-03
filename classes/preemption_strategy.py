from sumolib import checkBinary  # noqa
import traci  # noqa

from .logger import Logger


class PreemptionStrategy(object):
    def __init__(self, opt, orch):
        self.orch = orch
        self.options = opt
        self.restore_tls = {}
        self.infinity = False
        self.ev_entered = False
        self.ev_exited = False

    def setup(self, configuration, stats, evehicle):
        self.conf = configuration
        self.statistics = stats
        self.ev = evehicle
        self.mw = self.conf._mw
        self.logger = Logger(self.__class__.__name__).get()
        self.logger.info('Initiating')

    def configure(self):
        pass

    def execute_before_step_simulation(self, step):
        pass

    def get_colors(self, tl_current, tl_info, index):
        current_lights = self.mw.get_rgb_state(tl_current)
        if 'g' in current_lights.lower():
            current_light = 'g'
        elif 'y' in current_lights.lower():
            current_light = 'y'
        else:
            current_light = 'r'

        real_lights = tl_info['phases'][index]
        if 'g' in real_lights.lower():
            real_light = 'g'
        elif 'y' in real_lights.lower():
            real_light = 'y'
        else:
            real_light = 'r'

        return current_light, real_light

    def open_adj_tls(self, tl, phase, numberOfPhases):
        self.orch.open_adj_tls(tl, phase, numberOfPhases)

    def clear_adj_tls(self, tl):
        self.orch.clear_adj_tls(tl)

    def open_tl_at_time_by_cycles(self, cycle_quantity, tl_id, t):
        self.orch.open_tl_at_time_by_cycles(
            self.ev, cycle_quantity, tl_id, t, self.conf, self.infinity)

    def open_tl_at_time_by_cycles_by_time(self, cycle_quantity, tl_id, t, duration):
        self.orch.open_tl_at_time_by_cycles_by_time(
            self.ev, cycle_quantity, tl_id, t, self.conf, duration)

    def execute_step(self, step, ev_entered_in_simulation, in_simulation):
        if not self.ev_entered and not self.ev_exited and in_simulation:
            self.ev_entered = True

        if self.ev_entered and not self.ev_exited and not in_simulation:
            self.ev_exited = True

    def finish(self):
        self.orch.finish(self.ev)

    def ev_is_in_simulation(self):
        return self.ev_entered and not self.ev_exited

    # @staticmethod
    def instance_name(self):
        return 'evs!{}_seed!{}_alg!{}'.format(self.options.evs, self.options.seedsumo, self.options.algorithm)
