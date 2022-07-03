from classes.preemption_strategy import PreemptionStrategy
from classes.petri_util import PetriUtil

import numpy as np
import random
import math

class TimedPetriStrategy3(PreemptionStrategy):
  def configure(self):
    self.k = 0.149129457 #in veh/m = 240 vehicles per mile
    self.s = 0.444444444 #in veh/s = 1600 vehicles per hour
    self.a = 2.6 #https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html

    self.pn = None
    self.last_tl = None
    random.seed(self.options.seedsumo)

    self.edge_of_tl = {}
    self.executed_states = []
    self.infinity = True
    self.was_cancelled = False

    self.time_cancel = None
    self.retry = None
    self.retry_multiplier = 1

    self.time_stopped = 0

    self.first_time = True

    self.preemptive = {}

    self.min_gap = None

  def execute_step(self,step,ev_entered_in_simulation,in_simulation):
    super().execute_step(step,ev_entered_in_simulation,in_simulation)
    #self.sync_tls(step)
    
    if self.ev_entered and not self.ev_exited:

      if not self.min_gap:
        self.min_gap = self.mw.get_min_gap(self.ev)

      edges = self.mw.get_route_of_vehicle(self.ev)
      index = self.mw.get_route_index_of_vehicle(self.ev)

      current_tl_of_step = None
      while index < len(edges) and edges[index] not in self.conf.edges_with_tl:
        index = index + 1

      if index < len(edges):
        current_tl_of_step = self.conf.edges[edges[index]]['tl']['name'] 

      if self.pn == None or (self.retry is not None and (step >= self.retry)): #or \
                              #(self.mw.get_vehicle_acc(self.ev) > 0 and self.mw.get_vehicle_speed(self.ev) >= 0.1))):
        #if self.retry:
        #  self.retry_number += 1

        self.retry = None
        self.retry_multiplier = 1
        self.last_tl = current_tl_of_step
        self.time_stopped = 0

        self.executed_states = []
        self.edge_of_tl = {}        
        self.build_petri_net(step)

        for edge_id in self.conf.edges_with_tl:
          self.edge_of_tl[self.conf.edges[edge_id]['tl']['name']] = edge_id

      self.fire_transitions(step)

      p0_marks = ['_'.join(mark.split('_')[1:]) for mark in self.pn.get_marking() if 'p0_' in mark ]

      qcurrent = 0  

      for tl_p0 in p0_marks:
        tl_info = self.conf.edges[self.edge_of_tl[tl_p0]]['tl']

        if tl_p0 not in self.preemptive:
          for e in tl_info['edges']:
            hn = self.mw.get_halting_number_edge(e)
            avg_veh_length = self.mw.get_avg_veh_length_edge(e)
            qcurrent += hn*(avg_veh_length+self.min_gap)
          
          tflush = tl_info['y']['duration'] + tl_info['r']['duration']

          if qcurrent >= tl_info['qmax'] and self.mw.get_phase_of_tl(tl_p0) != tl_info['g']['index']:
            lane_vmax = tl_info['vmax']
            dlast = math.pow(lane_vmax,2)/(2*self.a)
            tlast = (qcurrent*self.k)/self.s
            open_duration = tlast + tflush
            open_duration += math.sqrt((2*qcurrent)/self.a) if qcurrent <= dlast else lane_vmax + (qcurrent - dlast)/lane_vmax
            opendur = max(open_duration,tl_info['g']['duration'])

            if self.pn.transition('t0_{}'.format(tl_p0)).min_time > step + opendur:
              self.open_tl_at_time_by_cycles_by_time(1,tl_p0,step,opendur)
              self.preemptive[tl_p0] = step + opendur
              qcurrent = 0
        elif step >= self.preemptive[tl_p0]:
          del self.preemptive[tl_p0]

      if current_tl_of_step is not None:
        if current_tl_of_step != self.last_tl:
          #check crossed TL
          next_tls = self.mw.get_next_tls(self.ev)
          #skip cluster
          if not (len(next_tls) > 0 and self.last_tl == next_tls[0][0]):           
            self.check_crossing(step)

          self.last_tl = current_tl_of_step
        elif self.pn is not None and self.retry is None:
          ev_speed = self.mw.get_vehicle_speed(self.ev)
          ev_acc = self.mw.get_vehicle_acc(self.ev)

          if (self.options.always or (self.options.clear and ev_speed <= 0.1 and ev_acc <= 0)) and not self.first_time:
            self.ask_to_clear(edges)
          else:
            self.first_time = False     

          if ev_speed <= 0.1 and ev_acc <= 0:
            self.time_stopped += 1
          else:
            self.retry = None
            #self.retry_multiplier = 1
            self.time_stopped = 0

          next_tls = self.mw.get_next_tls(self.ev)

          max_queue = 0 if len(next_tls) == 0 else next_tls[0][2]
          
          timeout = max((max_queue*self.k)/self.s,15)

          tl_info = self.conf.edges[self.edge_of_tl[current_tl_of_step]]['tl']          

          if self.time_stopped >= timeout:
            t = self.pn.transition('t5')
            if len(t.modes()) > 0 and  t.enabled(t.modes()[0]):
              t.fire(t.modes()[0])
              self.logger.info('firing t5 because {}, cancelling...'.format(current_tl_of_step))
              self.retry = step + (self.retry_multiplier*tl_info['ps_duration'][-1])
              #self.retry_multiplier += 1
            
      elif self.last_tl is not None:
        self.check_crossing(step)
        self.last_tl = None

    elif self.pn is not None:
      if 'p7' not in self.pn.get_marking():
        t = self.pn.transition('t5')
        if len(t.modes()) > 0 and t.enabled(t.modes()[0]):
          t.fire(t.modes()[0])
          self.was_cancelled = True
          self.retry = None
      else:        
        self.fire_transitions(step)
        if self.last_tl is not None:
          self.check_crossing(step)
          self.last_tl = None

  def fire_transitions(self, step):
    if self.pn is not None:
      self.pn.time(step)

      enabled_trans = [t for t in self.pn.transition() if 't3' not in t.name and 't5' not in t.name and len(t.modes()) > 0 and t.enabled(t.modes()[0])]

      for t in random.sample(enabled_trans, len(enabled_trans)):
        if len(t.modes()) == 0:
          continue

        print('firing {}...'.format(t.name))
        t.fire(t.modes()[0])

        for m in self.pn.get_marking():
          if 'p1_' in m and m not in self.executed_states:
            self.executed_states.append(m)
            edge_id =  self.edge_of_tl['_'.join(m.split('_')[1:])]
            self.open_tl_at_time_by_cycles(1,self.conf.edges[edge_id]['tl']['name'],step)

            for tl_adj in self.conf.edges[edge_id]['tl']['adj']:
              if tl_adj not in self.conf.tls:
                tl_adj_conf = self.conf.edges[edge_id]['tl']['adj'][tl_adj]
                self.open_adj_tls(tl_adj,tl_adj_conf['phase'],tl_adj_conf['numberOfPhases'])        

          if 'p4_' in m and m not in self.executed_states:
            self.executed_states.append(m)

            tl_to_restore = '_'.join(m.split('_')[1:])
            edge_id = self.edge_of_tl[tl_to_restore]

            if tl_to_restore in self.orch.active_evs_by_tl and self.ev in self.orch.active_evs_by_tl[tl_to_restore] and len(self.orch.active_evs_by_tl[tl_to_restore]) > 1:
              self.orch.active_evs_by_tl[tl_to_restore].remove(self.ev)
            else:            
              self.orch.schedule_sync(self.ev,tl_to_restore,self.conf,self.infinity)

            for tl_adj in self.conf.edges[edge_id]['tl']['adj']:
              if tl_adj not in self.conf.tls:
                self.clear_adj_tls(tl_adj)    

  def check_crossing(self, step):
    #check crossed TL
    if self.last_tl is not None: 
      trans_name = '{}_{}'.format('t3',self.last_tl)
      t = self.pn.transition(trans_name)
      if len(t.modes()) > 0 and t.enabled(t.modes()[0]):
        t.fire(t.modes()[0])
        print('firing {}...'.format(t.name))
        #self.retry_number = 1

        #if self.options.umt:
        edges = self.mw.get_route_of_vehicle(self.ev)
        index = self.mw.get_route_index_of_vehicle(self.ev)

        time_to_open_tls = self.get_min_times(index, edges, step)

        marks = self.pn.get_marking()

        for tl in time_to_open_tls:
          if '{}_{}'.format('p0',tl) in marks:
            t0 = self.pn.transition('{}_{}'.format('t0',tl))
            t0.update_min_time(time_to_open_tls[tl])
      elif self.retry is not None:
        self.pn = None

  def build_petri_net(self, step):
    edges = self.mw.get_route_of_vehicle(self.ev)
    index = self.mw.get_route_index_of_vehicle(self.ev)

    time_to_open_tls = self.get_min_times(index, edges, step)

    self.pn = PetriUtil().build_petri_net(self.conf,edges,index,time_to_open_tls)

  def get_min_times(self, index, edges, step):
    edges_speeds = []
    time_to_open_tls = {}
    halting_vehs = []
    avg_lengths = []

    ev_nominal_max_speed = self.mw.get_vehicle_max_speed(self.ev)    

    for i in range(index,len(edges)):
      edge = edges[i]
      halting_vehs.append(self.mw.get_halting_number_edge(edge))
      avg_lengths.append(self.mw.get_avg_veh_length_edge(edge))

      edges_speeds.append(self.conf.edges[edge]['vmax'])

      if edge in self.conf.edges_with_tl: 
        tl_info = self.conf.edges[edge]['tl']

        avg_vmax = np.mean(edges_speeds)
        qi = max(np.sum(halting_vehs)*(np.mean(avg_lengths)+self.min_gap),0)

        dlast = math.pow(avg_vmax,2)/(2*self.a)

        dtl = self.get_distance_to_tl(tl_info['name'],edge)

        ev_max_speed = min(ev_nominal_max_speed,avg_vmax)

        tflush = tl_info['y']['duration'] + tl_info['r']['duration']

        arrtime = dtl/ev_max_speed

        first_term = arrtime - (qi*self.k)/self.s

        if first_term <= 0:
          open_offset = 0
        elif qi <= dlast:
          open_offset = max((1-self.options.prt)*(first_term - math.sqrt((2*qi)/self.a) - tflush),0)
        else:
          open_offset = max((1-self.options.prt)*(first_term - avg_vmax/self.a - (qi-dlast)/avg_vmax - tflush),0)

        edges_speeds = []
        halting_vehs = []
        qi = 0          

        time_to_open_tls[tl_info['name']] = step + math.floor(open_offset)

        #qi = 0
    return time_to_open_tls

  def get_distance_to_tl(self,tl_current, tl_edge):
    next_tls = self.mw.get_next_tls(self.ev)
    if len(next_tls) > 0 and tl_current in next_tls[0][0]:
      return next_tls[0][2]

    distance = self.mw.get_distance_edge_vehicle(self.ev,tl_edge)

    if distance < 0 and tl_current in self.mw.get_junctions():
        pos_tl_x,pos_tl_y = self.mw.get_tl_position(tl_current)
        distance = self.mw.get_2d_distance_vehicle(self.ev,pos_tl_x,pos_tl_y)

    return distance

  def get_lanes(self,lane,edges,currlevel,maxlevel):
    if currlevel >= maxlevel:
      return set()

    e_id = '_'.join(lane.split('_')[0:-1])
    e_numlane = self.mw.get_num_lanes(e_id)

    next_lanes = set()

    for i in range(0,e_numlane):
      l_id = '{}_{}'.format(e_id,i)
      links_lid = self.mw.get_links_of_lane(l_id)

      next_lanes.add(l_id)

      for l in (l[0] for l in links_lid if '_'.join(l[0].split('_')[0:-1]) in edges):
        next_lanes |= self.get_lanes(l,edges,currlevel+1,maxlevel)

    return next_lanes

  def ask_to_clear(self, edges):
    e_id = self.mw.get_edge_of_vehicle(self.ev)

    num_lanes = self.mw.get_num_lanes(e_id)

    next_lanes = set()
    for li in range(0,num_lanes):
      next_lanes |= self.get_lanes('{}_{}'.format(e_id,li),edges,1,6)

    for lid in next_lanes:
      vehs = self.mw.get_vehicles_on_lane(lid)
      if len(vehs) > 0:
        last_veh = vehs[-1]
        links = self.mw.get_links_of_lane(lid)
        #links_outside_ev_route = [ l for l in links if '_'.join(l[0].split('_')[0:-1]) not in edges and l[2] == True and \
        #                          self.mw.get_vehicle_type(last_veh).split('_')[1] in self.mw.get_allowed_vehicles(l[0]) ]

        links_outside_ev_route = [ l for l in links if l[2] == True and \
                                  self.mw.get_vehicle_type(last_veh).split('_')[1] in self.mw.get_allowed_vehicles(l[0]) ]

        if last_veh != self.ev and len(links_outside_ev_route) > 1:
          #old_route = self.mw.get_route_of_vehicle(last_veh)
          #self.mw.change_vehicle_target(last_veh,self.mw.get_route_of_vehicle(last_veh)[-1])
          #new_route = self.mw.get_route_of_vehicle(last_veh)

          #if not np.array_equal(old_route,new_route):
          #  self.mw.set_vehicle_color(last_veh,(0,0,255))

          random.shuffle(links_outside_ev_route)
          for l in links_outside_ev_route:
            old_route = self.mw.get_route_of_vehicle(last_veh)

            new_route = self.mw.change_vehicle_target(last_veh,self.mw.get_route_of_vehicle(last_veh)[-1])

            i_last_veh = self.mw.get_route_index_of_vehicle(last_veh)
            new_route = self.mw.get_route('_'.join(l[0].split('_')[0:-1]),self.mw.get_route_of_vehicle(last_veh)[-1])

            self.mw.set_route_of_vehicle(last_veh,['_'.join(lid.split('_')[0:-1])] + list(new_route.edges))

            if not self.mw.is_route_of_vehicle_valid(last_veh):
              self.mw.set_route_of_vehicle(last_veh,old_route[i_last_veh:])
            else:
              self.mw.set_vehicle_color(last_veh,(0,0,255))
              self.statistics.update_affected_vehs(set(last_veh))
              break    

  def instance_name(self):
    return '{}_prt!{:.2f}_clear!{}_always!{}'.format(super().instance_name(),
            self.options.prt,
            'True' if self.options.clear else 'False',
            'True' if self.options.always else 'False',)    