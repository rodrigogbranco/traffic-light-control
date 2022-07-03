from classes.preemption_strategy import PreemptionStrategy

from .logger import Logger

class RfidPreemptionStrategy(PreemptionStrategy):

  def configure(self):
    self.__edges_with_preemption = [] 
    self.logger = Logger(self.__class__.__name__).get()
    self.current_edges_set = {}
    self.max_speed = None

  def execute_step(self,step,ev_entered_in_simulation,in_simulation):
    super().execute_step(step,ev_entered_in_simulation,in_simulation)
    if self.ev_entered and not self.ev_exited:
      self.conf.update_values()

      if not self.max_speed:
        self.max_speed = self.mw.get_vehicle_max_speed(self.ev)         

      if len(self.current_edges_set) == 0:     
        for edge_id in self.conf.edges_with_tl:
          tl_current = self.conf.edges[edge_id]['tl']['name']
          d = self.get_distance_to_tl(tl_current, edge_id)

          self.current_edges_set[edge_id] = (max(d-self.options.distancedetection,0))/self.max_speed + step - 1

      for edge_id in self.current_edges_set:
        if self.current_edges_set[edge_id] <= step and edge_id not in self.__edges_with_preemption:
          tl_current = self.conf.edges[edge_id]['tl']['name']

          d = self.get_distance_to_tl(tl_current, edge_id)

          self.current_edges_set[edge_id] = (max(d-self.options.distancedetection,0))/self.max_speed + step - 1

          if d <= self.options.distancedetection:
            self.open_tl_at_time_by_cycles(self.options.ncycles, tl_current, step)
            self.__edges_with_preemption.append(edge_id)

  def get_distance_to_tl(self,tl_current, tl_edge):
    if tl_current in self.mw.get_junctions():
      pos_ev_x, pos_ev_y = self.mw.get_vehicle_position(self.ev)
      pos_tl_x,pos_tl_y = self.mw.get_tl_position(tl_current)
      return self.mw.get_distance(pos_ev_x, pos_ev_y, pos_tl_x,pos_tl_y)

    next_tls = self.mw.get_next_tls(self.ev)
    
    if len(next_tls) > 0 and tl_current in next_tls[0][0]:
      return next_tls[0][2]

    return self.mw.get_distance_edge_vehicle(self.ev,tl_edge)

  def instance_name(self):
    return '{}_dd!{}_nc!{}'.format(super().instance_name(),self.options.distancedetection,self.options.ncycles)