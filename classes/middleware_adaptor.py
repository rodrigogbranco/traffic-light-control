from sumolib import checkBinary  # noqa
import traci  # noqa

import xml.etree.ElementTree
import numpy as np

import json

from classes.logger import Logger

class MiddlewareAdaptor:
    def __init__(self):    
        self.teleporteds = set()
        self._logger = Logger(self.__class__.__name__).get()
        self._reroute_edges = []        

    def set_options(self, **args):
        self._folder = args.pop("folder", None)

    def simulation_is_running(self):
        return traci.simulation.getMinExpectedNumber() > 0

    def get_time(self):
        return int(traci.simulation.getTime())

    def get_nvec(self):
        return traci.vehicle.getIDCount()

    def do_simulation_step(self):
        traci.simulationStep()

    def get_distance_travelled_by_vehicle(self,veh):
        return traci.vehicle.getDistance(veh)

    def vehicle_was_teleported(self,veh):
        self.teleporteds |= set(traci.simulation.getStartingTeleportIDList())
        return veh in self.teleporteds        

    def get_teleported_vehicles(self):
        return self.teleporteds

    def vehicle_in_simulation(self,veh):
        try:
            return self.get_edge_of_vehicle(veh) != ''
        except traci.exceptions.TraCIException:
            return False

    def cars_in_simulation(self):
        return traci.vehicle.getIDList()

    def finish_simulation(self):
        traci.close()

    def get_departed_vehs_number(self):
        return traci.simulation.getDepartedNumber()

    def get_edges_id(self):
        return traci.edge.getIDList()

    def get_route_of_vehicle_from_file(self,veh):
        _routes_file = xml.etree.ElementTree.parse('{}/osm.emergency.rou.xml'.format(self._folder)).getroot()
        route = _routes_file.find('./vehicle[@id="{}"]/route'.format(veh))

        return np.array(route.get('edges').split(' ')) if route != None else np.array([]) 

    def get_route_of_vehicle(self,veh):
        return np.array(traci.vehicle.getRoute(veh))

    def get_edges_to_reroute(self):
        if len(self._reroute_edges) == 0:
            _net_file = xml.etree.ElementTree.parse('{}/../osm.net.xml'.format(self._folder)).getroot()
            self._reroute_edges = [ e.get('id') for e in _net_file.findall('./edge[@type="highway.motorway"]') + \
                            _net_file.findall('./edge[@type="highway.primary"]') + \
                            _net_file.findall('./edge[@type="highway.secondary"]') + \
                            _net_file.findall('./edge[@type="highway.tertiary"]') ]

        return self._reroute_edges

    def set_route_of_vehicle(self,veh,new_route):
        traci.vehicle.setRoute(veh,new_route)
    
    def get_net_file(self):
        return xml.etree.ElementTree.parse('{}/../osm.net.xml'.format(self._folder)).getroot()

    def get_tls_json(self):
        file_tmp = open('{}/../osm.tls.json'.format(self._folder),'r')
        tls = json.loads(file_tmp.read())
        file_tmp.close() 
        return tls

    def get_edge_of_vehicle(self,veh):
        return traci.vehicle.getRoadID(veh)

    def get_lane_of_vehicle(self,veh):
        return traci.vehicle.getLaneID(veh)

    def get_vehicle_speed(self,veh):
        return traci.vehicle.getSpeed(veh)

    def get_vehicle_acc(self,veh):
        return traci.vehicle.getAcceleration(veh)

    def get_route_index_of_vehicle(self,veh):
        return traci.vehicle.getRouteIndex(veh)

    def get_lane_index_of_of_vehicle(self,veh):
        return traci.vehicle.getLaneIndex(veh)

    def is_route_of_vehicle_valid(self,veh):
        return traci.vehicle.isRouteValid(veh)

    def get_leader_of_vehicle(self,veh):
        return traci.vehicle.getLeader(veh)

    def vehicle_could_change_lane(self,veh,direction):
        return traci.vehicle.couldChangeLane(veh,direction)

    def change_vehicle_lane(self,veh,index,when):
        traci.vehicle.changeLane(veh,index,when)

    def get_vehicle_type(self,veh):
        return traci.vehicle.getTypeID(veh)

    def get_vehicle_length(self,veh):
        return traci.vehicle.getLength(veh)

    def change_vehicle_target(self,veh,target):
        traci.vehicle.changeTarget(veh,target)

    def get_vehicles_on_lane(self,lane):
        return traci.lane.getLastStepVehicleIDs(lane)
    
    def get_vehicle_on_edge(self,edge):
        return traci.edge.getLastStepVehicleIDs(edge)

    def get_max_speed_of_lane(self,lane):
        return traci.lane.getMaxSpeed(lane)

    def get_min_gap(self,veh):
        return traci.vehicle.getMinGap(veh)

    def get_vehicle_max_speed(self,veh):
        return traci.vehicle.getMaxSpeed(veh)

    def get_vehicle_max_acc(self,veh):
        return traci.vehicle.getAccel(veh)        

    def get_length_of_lane(self,lane):
        return traci.lane.getLength(lane)

    def get_links_of_lane(self,lane):
        return traci.lane.getLinks(lane)

    def get_controlled_links_of_tl(self,tl):
        return traci.trafficlight.getControlledLinks(tl)

    def get_phase_of_tl(self,tl):
        return traci.trafficlight.getPhase(tl)

    def set_phase_of_tl(self,tl,phase):
        traci.trafficlight.setPhase(tl,phase)

    def set_phase_duration_of_tl(self,tl,duration):
        traci.trafficlight.setPhaseDuration(tl,duration)

    def get_phase_duration_of_tl(self,tl):
        return traci.trafficlight.getPhaseDuration(tl)

    def get_next_switch_of_tl(self,tl):
        return traci.trafficlight.getNextSwitch(tl)

    def get_allowed_vehicles(self,lane):
        return traci.lane.getAllowed(lane)

    def get_route(self,input,output):
        return traci.simulation.findRoute(input,output)

    def get_complete_definition_of_tl(self,tl):
        return traci.trafficlight.getCompleteRedYellowGreenDefinition(tl)

    def set_program_of_tl(self,tl,program):
        traci.trafficlight.setProgram(tl,program)

    def set_complete_definition_of_tl(self,tl,program):
        traci.trafficlight.setCompleteRedYellowGreenDefinition(tl,program)

    def get_rgb_state(self,tl):
        return traci.trafficlight.getRedYellowGreenState(tl)

    def get_program_of_tl(self,tl):
        return traci.trafficlight.getProgram(tl)

    def get_controlled_lanes(self,tl):
        return traci.trafficlight.getControlledLanes(tl)

    def get_lane_occupancy(self,lane):
        return traci.lane.getLastStepOccupancy(lane)

    def get_lane_mean_speed(self,lane):
        return traci.lane.getLastStepMeanSpeed(lane)

    def set_lane_max_speed(self,lane,vmax):
        traci.lane.setMaxSpeed(lane,vmax)

    def get_halting_number(self,lane):
        return traci.lane.getLastStepHaltingNumber(lane)

    def get_halting_number_edge(self,edge):
        return traci.edge.getLastStepHaltingNumber(edge)

    def get_avg_veh_length(self,lane):
        return traci.lane.getLastStepLength(lane)

    def get_avg_veh_length_edge(self,edge):
        return traci.edge.getLastStepLength(edge)       

    def get_edge_occupancy(self,edge):
        return traci.edge.getLastStepOccupancy(edge)

    def get_edge_mean_speed(self,edge):
        return traci.edge.getLastStepMeanSpeed(edge)

    def get_num_lanes(self,edge):
        return traci.edge.getLaneNumber(edge)

    def get_next_tls(self,veh):
        return traci.vehicle.getNextTLS(veh)

    def get_distance_edge_vehicle(self,veh,edge):
        return traci.vehicle.getDrivingDistance(veh,edge,1.0)

    def get_junctions(self):
        return traci.junction.getIDList()

    def get_tl_position(self,tl):
        return traci.junction.getPosition(tl)

    def get_vehicle_position(self,veh):
        return traci.vehicle.getPosition(veh)

    def get_2d_distance_vehicle(self,veh,x,y):
        return traci.vehicle.getDrivingDistance2D(veh,x,y)

    def get_distance(self,pos_ev_x, pos_ev_y, pos_tl_x,pos_tl_y):
        return traci.simulation.getDistance2D(pos_ev_x, pos_ev_y, pos_tl_x,pos_tl_y, False, False)

    def set_vehicle_color(self,veh,color):
        traci.vehicle.setColor(veh, color)

    def track_vehicle(self,veh,gui,primary):
        if gui and primary:
            traci.gui.trackVehicle('View #0',veh)
            traci.gui.setZoom('View #0',10000)
            self.set_vehicle_color(veh, (255,0,0))
        elif gui:
            self.set_vehicle_color(veh, (255,0,255))