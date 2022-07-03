import math
from classes.preemption_strategy import PreemptionStrategy


class KapustaImpStrategy(PreemptionStrategy):
    # constants: Marshall, P.S. and W.D. Berg, Design Guidelines for Railroad Preemption at Signalized Intersections. Institute of Transportation Engineers Journal, 1997.
    def configure(self):
        self.last_tl = None
        self.jam_density = 0.149129457  # in veh/m = 240 vehicles per mile
        self.saturation_flow = 0.444444444  # in veh/s = 1600 vehicles per hour
        self.accel = 2.6  # https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html
        self.t_alpha = 3
        self.t_beta = 0.5
        self.cycle_length = 90
        self.s_alpha = 10
        self.s_beta = 15
        self.program_bkp = {}
        self.all_active_tls = None
        self.ev_vmax = None
        self.infinity = True
        self.activated_tls = set()
        self.k = 0.149129457  # in veh/m = 240 vehicles per mile
        self.s = 0.444444444  # in veh/s = 1600 vehicles per hour
        self.a = 2.6  # https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html

    def execute_step(self, step, ev_entered_in_simulation, in_simulation):
        super().execute_step(step, ev_entered_in_simulation, in_simulation)
        # self.sync_tls(step)

        if self.ev_entered and not self.ev_exited:
            if self.ev_vmax == None:
                self.ev_vmax = self.mw.get_vehicle_max_speed(self.ev)

            if self.all_active_tls == None:
                self.all_active_tls = [
                    self.conf.edges[e]["tl"]["name"] for e in self.conf.edges_with_tl
                ]
                for tl in self.all_active_tls:
                    self.program_bkp[tl] = self.mw.get_complete_definition_of_tl(tl)

            edges = self.mw.get_route_of_vehicle(self.ev)
            index = self.mw.get_route_index_of_vehicle(self.ev)

            for i in range(index, len(edges)):
                if edges[i] in self.conf.edges_with_tl:
                    tl = self.conf.edges[edges[i]]["tl"]["name"]
                    intersection_distance = self.get_distance_to_tl(tl, edges[i])

                    lane = "{}_0".format(edges[i])

                    lane_vmax = self.mw.get_max_speed_of_lane(lane)
                    max_v = max(self.ev_vmax, lane_vmax)

                    arrival_time = intersection_distance / max_v

                    hn = self.mw.get_halting_number(lane)
                    avg_veh_length = self.mw.get_avg_veh_length(lane)

                    queue_length = hn * avg_veh_length

                    qflush = 0

                    if queue_length > 0:
                        qflush = (queue_length * self.k) / self.s
                        dlast = math.pow(max_v, 2) / (2 * self.a)
                        if queue_length <= dlast:
                            qflush += math.sqrt((2 * queue_length) / self.a)
                        else:
                            qflush += max_v / self.a - (queue_length - dlast) / max_v

                    tflush = (
                        self.conf.edges[edges[i]]["tl"]["y"]["duration"]
                        + self.conf.edges[edges[i]]["tl"]["r"]["duration"]
                    )

                    if (
                        arrival_time - qflush - tflush <= 0
                        and tl not in self.activated_tls
                    ):
                        self.open_tl_at_time_by_cycles(1, tl, step)
                        self.activated_tls.add(tl)

            for i in range(0, index - 1):
                if (
                    edges[i] in self.conf.edges_with_tl
                    and self.conf.edges[edges[i]]["tl"]["name"] in self.all_active_tls
                ):
                    tl_name = self.conf.edges[edges[i]]["tl"]["name"]
                    self.all_active_tls.remove(tl_name)
                    self.orch.schedule_sync(self.ev, tl_name, self.conf, self.infinity)

        if self.ev_entered and self.ev_exited and len(self.all_active_tls) > 0:
            for edge in self.conf.edges_with_tl:
                tl_name = self.conf.edges[edge]["tl"]["name"]
                if tl_name in self.all_active_tls:
                    self.all_active_tls.remove(tl_name)
                    self.orch.schedule_sync(self.ev, tl_name, self.conf, self.infinity)

    def get_distance_to_tl(self, tl_current, tl_edge):
        next_tls = self.mw.get_next_tls(self.ev)
        if len(next_tls) > 0 and tl_current in next_tls[0][0]:
            return next_tls[0][2]

        distance = self.mw.get_distance_edge_vehicle(self.ev, tl_edge)

        if distance < 0 and tl_current in self.mw.get_junctions():
            pos_tl_x, pos_tl_y = self.mw.get_tl_position(tl_current)
            distance = self.mw.get_2d_distance_vehicle(self.ev, pos_tl_x, pos_tl_y)

        return distance
