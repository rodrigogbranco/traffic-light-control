from classes.preemption_strategy import PreemptionStrategy

import math

class KapustaStrategy2(PreemptionStrategy):
    #constants: Marshall, P.S. and W.D. Berg, Design Guidelines for Railroad Preemption at Signalized Intersections. Institute of Transportation Engineers Journal, 1997.
    def configure(self):
        self.last_tl = None
        self.jam_density = 0.149129457 #in veh/m = 240 vehicles per mile
        self.saturation_flow = 0.444444444 #in veh/s = 1600 vehicles per hour
        self.accel = 2.6 #https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html
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

    def execute_step(self,step,ev_entered_in_simulation,in_simulation):
        super().execute_step(step,ev_entered_in_simulation,in_simulation)
        #self.sync_tls(step)

        if self.ev_entered and not self.ev_exited:
            if self.ev_vmax == None:
                self.ev_vmax = self.mw.get_vehicle_max_speed(self.ev)

            if self.all_active_tls == None:
                self.all_active_tls = [ self.conf.edges[e]['tl']['name'] for e in self.conf.edges_with_tl ]
                for tl in self.all_active_tls:
                    self.program_bkp[tl] = self.mw.get_complete_definition_of_tl(tl)

            edges = self.mw.get_route_of_vehicle(self.ev)
            index = self.mw.get_route_index_of_vehicle(self.ev)

            for i in range(index,len(edges)):
                if edges[i] in self.conf.edges_with_tl:
                    tl = self.conf.edges[edges[i]]['tl']['name']
                    intersection_distance = self.get_distance_to_tl(tl,edges[i])

                    lane = '{}_{}'.format(edges[i],0)

                    lane_vmax = self.mw.get_max_speed_of_lane(lane)
                    max_v = max(self.ev_vmax,lane_vmax)

                    ev_acc = self.mw.get_vehicle_acc(self.ev)

                    if ev_acc > 0:
                        
                        arrival_time = max_v/ev_acc + (intersection_distance - (max_v*max_v)/(2*ev_acc))/max_v
                    else:
                        arrival_time = intersection_distance/max_v

                    if self.t_alpha*self.cycle_length > arrival_time and arrival_time > self.t_beta * self.cycle_length:
                        hn = self.mw.get_halting_number(lane)
                        avg_veh_length = self.mw.get_avg_veh_length(lane)

                        queue_length = hn*avg_veh_length

                        if queue_length > self.s_alpha:
                            index_of_g = self.conf.edges[edges[i]]['tl']['g']['index']

                            if self.mw.get_phase_of_tl(tl) == index_of_g:
                                remain = self.mw.get_phase_duration_of_tl(tl)
                                self.orch.set_phase_duration_of_tl(step,tl,1.10*remain)

                        if queue_length > self.s_beta:
                            index_of_g = self.conf.edges[edges[i]]['tl']['g']['index']
                            if self.mw.get_phase_of_tl(tl) != index_of_g:
                                remain = self.mw.get_phase_duration_of_tl(tl)
                                self.orch.set_phase_duration_of_tl(step,tl,0.90*remain)

                    if arrival_time < self.t_beta * self.cycle_length:
                        if tl not in self.activated_tls:
                            self.open_tl_at_time_by_cycles(1,tl,step)
                            self.activated_tls.add(tl)

            for i in range(0,index-1):
                if edges[i] in self.conf.edges_with_tl and self.conf.edges[edges[i]]['tl']['name'] in self.all_active_tls:
                    tl_name = self.conf.edges[edges[i]]['tl']['name']
                    self.all_active_tls.remove(tl_name)
                    self.orch.schedule_sync(self.ev,tl_name,self.conf,self.infinity)

        if self.ev_entered and self.ev_exited and len(self.all_active_tls) > 0:
            for edge in self.conf.edges_with_tl:
                tl_name = self.conf.edges[edge]['tl']['name']
                if tl_name in self.all_active_tls:
                    self.all_active_tls.remove(tl_name)
                    self.orch.schedule_sync(self.ev,tl_name,self.conf,self.infinity)


    def get_distance_to_tl(self,tl_current, tl_edge):
        next_tls = self.mw.get_next_tls(self.ev)
        if len(next_tls) > 0 and tl_current in next_tls[0][0]:
            return next_tls[0][2]

        distance = self.mw.get_distance_edge_vehicle(self.ev,tl_edge)            

        if distance < 0 and tl_current in self.mw.get_junctions():
            pos_tl_x,pos_tl_y = self.mw.get_tl_position(tl_current)
            distance = self.mw.get_2d_distance_vehicle(self.ev,pos_tl_x,pos_tl_y)

        return distance           