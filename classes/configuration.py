from classes.logger import Logger

import numpy as np
import math

class Configuration():

  @property
  def edges(self):
    return self._edges

  @property
  def edges_order(self):
    return self._edges_order

  @property
  def edges_with_tl(self):
    return self._edges_with_tl

  @property
  def tls(self):
    return [self._edges[edge]['tl']['name'] for edge in self._edges_with_tl]

  def set_staticdynamic(self):
    self.staticdynamic = True

  def __init__(self, ev, folder, mw):
    self._mw = mw
    self._folder = folder
    self._ev = ev
    self._logger = Logger(self.__class__.__name__).get()

    self._edges_order = np.array([])
    self._edges_with_tl = []
    self.edges_to_reroute = []
    self.staticdynamic = False

    self.k = 0.149129457 #in veh/m = 240 vehicles per mile
    self.s = 0.444444444 #in veh/s = 1600 vehicles per hour
    self.a = 2.6 #https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html    

  def update_values(self):
    new = self._mw.get_route_of_vehicle(self._ev)  
    
    if not np.array_equiv(self._edges_order,new):
      if self.staticdynamic:
        new_route = self._mw.get_route_of_vehicle_from_file(self._ev)
        if new_route.size > 0:
          self._mw.set_route_of_vehicle(self._ev,new_route)

      new = self._mw.get_route_of_vehicle(self._ev)

      self._logger.debug('old')
      self._logger.debug(self._edges_order)
      self._logger.debug('new')
      self._logger.debug(new)

      self._edges_order = self._mw.get_route_of_vehicle(self._ev)
      self.compute_values()
      return True

    return False

  def compute_values(self):
    self.edges_to_reroute = self._mw.get_edges_to_reroute()

    self._edges_with_tl = []

    self._edges = {}
    self._tls = set()

    self._logger.debug(self._edges_order)

    tls_already_used = {}

    index = self._mw.get_route_index_of_vehicle(self._ev)

    my_type = self._mw.get_vehicle_type(self._ev)
    if '_' in my_type:
      my_type = my_type.split('_')[1]

    edges_of_tl = []

    #netfile = self._mw.get_net_file()
    tlsjson = self._mw.get_tls_json()

    conn_tls = []

    for i in range(index,len(self._edges_order)):
      edge_name = self._edges_order[i]
      edges_of_tl.append(edge_name)
      self._edges[edge_name] = {}
      current_edge = self._edges[edge_name]
      lane = edge_name+'_0'

      #path = './connection[@from="{}"]'.format(edge_name)

      #if i+1 < len(self._edges_order):
      #    path += '[@to="{}"]'.format(self._edges_order[i+1])

      conn_tls.append([])

      if i+1 < len(self._edges_order):
        if edge_name in tlsjson:
          if self._edges_order[i+1] in tlsjson[edge_name]:
            conn_tls[i].append(tlsjson[edge_name][self._edges_order[i+1]])

      #self._logger.debug(path)   
      #connections = netfile.findall(path)      

      #conn_tls[i] = [ c.get('tl') for c in connections ]    

    #netfile = None

    for i in range(index,len(self._edges_order)):
      edge_name = self._edges_order[i]
      edges_of_tl.append(edge_name)
      self._edges[edge_name] = {}
      current_edge = self._edges[edge_name]
      lane = edge_name+'_0'

      current_edge['vmax'] = self._mw.get_max_speed_of_lane(lane)
      current_edge['length'] = self._mw.get_length_of_lane(lane)

      self._logger.debug('{} {} {}'.format(edge_name,current_edge['vmax'],current_edge['length']))

      tl = None
      link_index = -1
      lane_in = None
      lane_out = None
      input_links_edge = []
      for tls in conn_tls[i]:
        if tl is not None:
          break

        if tls and i+1 < len(self._edges_order):
          controlled_links = self._mw.get_controlled_links_of_tl(tls)
          for li in range(len(controlled_links)):
            link_tuple = controlled_links[li]
            if len(link_tuple) > 0:
              if edge_name in link_tuple[0][0]:
                input_links_edge.append(li)

              if edge_name in link_tuple[0][0] and self._edges_order[i+1] in link_tuple[0][1] and \
                my_type in self._mw.get_allowed_vehicles(link_tuple[0][0]):
                tl = tls
                link_index = li
                lane_in = link_tuple[0][0]
                lane_out = link_tuple[0][1]

      conn_tls[i] = {}

      if tl != None:
        if tl in tls_already_used:
          has_tl = [ edge for edge in self._edges if 'tl' in self._edges[edge] and self._edges[edge]['tl']['name'] == tl ]
          if len(has_tl) > 0:
            edge_in_use = has_tl[0]
            self._edges[edge_in_use]['tl']['cluster'] = True

            controlled_links = self._mw.get_controlled_links_of_tl(tl)
            for li in range(len(controlled_links)):
              link_tuple = controlled_links[li]
              if edge_name in link_tuple[0][0] and self._edges_order[i+1] in link_tuple[0][1]:
                if my_type in self._mw.get_allowed_vehicles(link_tuple[0][0]):
                  self._edges[edge_in_use]['tl']['other_link_indexes'].append(li)
                  all_indexes = self._edges[edge_in_use]['tl']['other_link_indexes']
                  g_index = self._edges[edge_in_use]['tl']['g']['index']

                  all_programs = self._mw.get_complete_definition_of_tl(tl)
                  my_program = [ program for program in all_programs if program.programID == current_program ][0]
                  lights = my_program.phases[g_index].state
                  if lights[li].upper() == 'G':
                    break
                  else:
                    for p in range(0,len(my_program.phases)):
                      state = my_program.phases[p].state.upper()
                      all_green = True
                      for x in all_indexes:
                        if state[x] != 'G':
                          all_green = False
                          break
                      
                      if all_green:
                        self._edges[edge_in_use]['tl']['g']['index'] = p
                        self._edges[edge_in_use]['tl']['g']['duration'] = my_program.phases[p].duration
                        break


          continue

        tls_already_used[tl] = edge_name
        self._edges_with_tl.append(edge_name)
        self._tls.add(tl)
        current_edge['tl'] = {}
        current_edge['tl']['name'] = tl
        current_edge['tl']['cluster'] = False
        current_edge['tl']['lane_in'] = lane_in
        current_edge['tl']['lane_out'] = lane_out
        current_edge['tl']['link_index'] = link_index
        current_edge['tl']['other_link_indexes'] = []
        current_edge['tl']['other_link_indexes'].append(link_index)


        current_program = self._mw.get_program_of_tl(tl)

        all_programs = self._mw.get_complete_definition_of_tl(tl)
        my_program = [ program for program in all_programs if program.programID == current_program ][0]
        self._logger.debug(my_program.phases[0].duration)
        
        right_index = int(link_index)
        lights_sequence = list(map((lambda ls: ls.state[right_index].upper()), my_program.phases))

        green_phase_index = lights_sequence.index('G')
        count_g = my_program.phases[green_phase_index].state.upper().count('G')
        
        edge_g = 0

        for l_index in range(len(lights_sequence)):
          count_edge_g = 0
          for x in input_links_edge:
            if my_program.phases[l_index].state[x].upper() == 'G':
              count_edge_g = count_edge_g + 1

          if (lights_sequence[l_index].upper() == 'G' and count_edge_g > edge_g) or \
            (count_edge_g == edge_g and my_program.phases[l_index].state.upper().count('G') > count_g):
            #and my_program.phases[l_index].state.upper().count('G') > count_g:
            count_g = my_program.phases[l_index].state.upper().count('G')
            edge_g = count_edge_g
            green_phase_index = l_index       


        self.define_parameters(green_phase_index, lights_sequence, current_edge['tl'], current_edge, my_program)

        tg = current_edge['tl']['g']['duration']
        tf = current_edge['tl']['y']['duration'] + current_edge['tl']['r']['duration']

        delta = (math.sqrt(2*self.a*self.k*self.s**3*abs(tg - tf) + self.s**4)/self.a)

        qmaxneg = (-delta + (self.s**2)/self.a + self.k*self.s*abs(tg - tf))/(self.k**2)
        qmaxpos = ( delta + (self.s**2)/self.a + self.k*self.s*abs(tg - tf))/(self.k**2)

        if qmaxneg >= 0 and qmaxpos >= 0:
          qmax = max(min(qmaxneg,qmaxpos),0)

        current_edge['tl']['qmax'] = min(qmax,current_edge['tl']['length'])
        current_edge['tl']['edges'] = edges_of_tl
        edges_of_tl = []

  def is_not_car_allowed(self,alloweds):
    not_cars = ['tram', 'rail_urban', 'rail', 'rail_electric', 'ship']

    return len([a for a in not_cars if a in alloweds]) > 0

  def define_parameters(self, green_phase_index, lights_sequence, tl_info, current_edge, my_program):
    safe_phase_index = (green_phase_index - 2) % len(lights_sequence)
    red_phase_index = (green_phase_index - 1) % len(lights_sequence)
    self._logger.debug(str(green_phase_index)+' '+str(safe_phase_index)+' '+str(red_phase_index))

    tl_info['g'] = {}
    tl_info['g']['index'] = green_phase_index
    tl_info['g']['duration'] = my_program.phases[green_phase_index].duration

    tl_info['y'] = {}
    tl_info['y']['index'] = safe_phase_index
    tl_info['y']['duration'] = my_program.phases[safe_phase_index].duration

    tl_info['r'] = {}
    tl_info['r']['index'] = red_phase_index
    tl_info['r']['duration'] = my_program.phases[red_phase_index].duration

    self.define_durations(tl_info, my_program)

    tl_time = tl_info['y']['duration'] + tl_info['r']['duration'] + tl_info['g']['duration']

    self._logger.debug(current_edge['vmax'])
    self._logger.debug(tl_time)

    tl_info['s_detection'] = float(current_edge['vmax'])*float(tl_time)

    tl_info['vmax'] = current_edge['vmax']
    tl_info['length'] = current_edge['length']

    self._logger.debug(current_edge['tl'])

  def define_durations(self, tl_info, my_program):
    tl_info['ps_duration'] = []
    tl_info['phases'] = []
    tl_info['durations'] = []

    for t in range(len(my_program.phases)):
      tl_info['phases'].append(my_program.phases[t].state)
      tl_info['durations'].append(my_program.phases[t].duration)
      if t == 0:
        tl_info['ps_duration'].append(my_program.phases[t].duration)
      else:
        tl_info['ps_duration'].append(tl_info['ps_duration'][t-1] + my_program.phases[t].duration)
