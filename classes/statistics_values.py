import xml.etree.ElementTree
import numpy
import os
from .logger import Logger
import json
import collections
import sys
import pandas as pd
import numpy as np, scipy.stats as st

from sumolib import checkBinary  # noqa
import traci  # noqa

class StatisticsValues:
  def __init__(self, folder, trip_path, trip_file, alg, evs=0):
    self.__folder = folder
    self.__trip_file = trip_file
    self.__trip_path = trip_path
    self._logger = Logger(self.__class__.__name__).get()
    self.__algorithm = alg

    self.teleported = set()

    self.affected_vehs = set()    

    self.tls_active_time = {}

    self.evs_data = {}    

    self.evs = []

    self.stats = {}

    self.gps = {'scenario' : [], 'ev' : [], 'step' : [], 'lon' : [], 'lat' : []}

    self.edges_id = None

  def compute_stats(self,step,current_vehs,current_departed,edge,value):
    self.stats[step] = {}
    self.stats[step]['curr'] = current_vehs
    self.stats[step]['dep'] = current_departed
    self.stats[step]['e'] = edge
    self.stats[step]['eval'] = value

  def load_and_parse_xmls(self,evs):
    xml_file = xml.etree.ElementTree.parse('{}/osm.emergency.trips.xml'.format(self.__folder)).getroot()
    route_file = xml.etree.ElementTree.parse('{}/osm.emergency.rou.xml'.format(self.__folder)).getroot()

    for ev in evs.split(','):
      self.evs.append(ev)
      self.evs_data[ev] = {}

      check_ev = xml_file.findall('trip[@id="{}"]'.format(ev))

      self.evs_data[ev] = check_ev[0].attrib

      self.evs_data[ev]['route'] = route_file.findall('./vehicle[@id="{}"]/route'.format(ev))[0].get('edges')

      if len(check_ev) <= 0:
        sys.exit("ERROR: EV not found in trip file")

      self.evs_data[ev]['was_teleported'] = False

      self.evs_data[ev]['crossed_tls_by_ev'] = 0

      self.evs_data[ev]['n_when_ev_enter'] = -1
      self.evs_data[ev]['n_when_ev_left'] = -1

      self.evs_data[ev]['ev_start'] = -1
      self.evs_data[ev]['ev_end'] = -1

      self.evs_data[ev]['last_edge'] = None
      self.evs_data[ev]['last_lane'] = None

      self.evs_data[ev]['distance_travelled'] = -1
      
      self.evs_data[ev]['number_of_vehicles'] = 0

      self.evs_data[ev]['final_time'] = -1

      self.evs_data[ev]['tls_active_time_mean'] = 0
      self.evs_data[ev]['tls_active_time_interval'] = 0

      self.evs_data[ev]['ev_ttt'] = -1
      self.evs_data[ev]['ev_timeloss'] = -1

      self.evs_data[ev]['ev_avg_speed'] = 0

      self.evs_data[ev]['gps'] = {}

    xml_file = None

  def set_gps_step(self,scenario,ev,step,lat,lon):
    self.gps['scenario'].append(scenario)
    self.gps['ev'].append(ev)
    self.gps['step'].append(step)
    self.gps['lat'].append(lat)
    self.gps['lon'].append(lon)

  def set_tl_number(self,n,evs):
    for ev in evs.split(','):
      self.evs_data[ev]['tl_logics'] = n

  def update_affected_vehs(self,vehs):
    self.affected_vehs |= vehs

  def set_active_time(self,times):
    self.tls_active_time = times
    
  def print_tuple(self, label, provided_list):
    size = len(provided_list)
    if size > 0:
      modified_list = numpy.array(provided_list).astype(numpy.float)
      avg = numpy.mean(modified_list)
      var = numpy.var(modified_list)
      std = numpy.std(modified_list)
      msg = '{0}\t\t{1}\t\t{2:.2f}\t\t{3:.2f}\t\t{4:.2f}'
      self._logger.info(msg.format(label, size, avg, var, std))
    else:
      self._logger.info('empty list')

  def set_crossed_tls(self,ev,value):
    self.evs_data[ev]['crossed_tls_by_ev'] = value

  def get_results(self, ev, final_time):
    #self.evs_data[ev]['final_time'] = final_time
    xml_file = xml.etree.ElementTree.parse(self.__trip_file).getroot()
    tripsinfo = xml_file.findall('tripinfo')
    self.evs_data[ev]['number_of_vehicles'] = len(tripsinfo)
    ev_trip = [x for x in tripsinfo if x.attrib['id'] == ev]
    if len(ev_trip) <= 0:
      self._logger.warn('EV {} is not in tripinfo file!'.format(ev))
    else:
      ev_trip = ev_trip[0]
      self.evs_data[ev]['ev_ttt'] = ev_trip.attrib['duration']
      self.evs_data[ev]['ev_timeloss'] = ev_trip.attrib['timeLoss']
      self.evs_data[ev]['ev_avg_speed'] = float(self.evs_data[ev]['distance_travelled'])/float(self.evs_data[ev]['ev_ttt'])
      self._logger.info('###RESULTS - Algorithm => {}###'.format(self.__algorithm))
      self._logger.info('EV: {}'.format(ev))
      self._logger.info('Number of TL {}'.format(self.evs_data[ev]['tl_logics']))
      self._logger.info('total number of vehicles: {}'.format(self.evs_data[ev]['number_of_vehicles']))
      self._logger.info('EV Total travel time: {}'.format(self.evs_data[ev]['ev_ttt']))
      self._logger.info('EV Time loss: {}'.format(self.evs_data[ev]['ev_timeloss']))
      self._logger.info('number of tls crossed by ev: {}'.format(self.evs_data[ev]['crossed_tls_by_ev']))
      self._logger.info('Label\t\t#\t\tAvg\t\tVar\t\tStd')
      other_trip_time = [x.attrib['duration'] for x in tripsinfo if x.attrib['id'] != ev]
      self.print_tuple('Other vehicles - Total Trip Time', other_trip_time)
      other_time_loss = [x.attrib['timeLoss'] for x in tripsinfo if x.attrib['id'] != ev]
      self.print_tuple('Other vehicles - Time Loss', other_time_loss)
      self._logger.info('Final time of simulation: {}'.format(final_time))
      self._logger.info('Times EV - enter: {} left: {}'.format(self.evs_data[ev]['ev_start'],self.evs_data[ev]['ev_end']))
      self._logger.info('Number of vehicles - enter: {} left: {}'.format(self.evs_data[ev]['n_when_ev_enter'],self.evs_data[ev]['n_when_ev_left']))
      self._logger.info('Number of teleported vehicles: {}'.format(len(self.teleported)))
      self._logger.info('Number of affected vehicles: {}'.format(len(self.affected_vehs)))
      #self._logger.info('Number of vehicles affected by ev: {}'.format(len(self.evs_data[ev]['vehicles_affected_by_ev'])))
      self._logger.info('Ev was teleported: {}'.format(self.evs_data[ev]['was_teleported']))
      if self.evs_data[ev]['was_teleported']:
        self._logger.info('Last edge of {}: {}'.format(ev,self.evs_data[ev]['last_edge']))
      self._logger.info('Distance travelled: {}'.format(self.evs_data[ev]['distance_travelled']))
      self._logger.info('EV Avg Speed: {}'.format(self.evs_data[ev]['ev_avg_speed']))   

    self._logger.info('###RESULTS###')

  def print_summary(self,ev):
    self._logger.info('{} had entered when t={} left the network when t={}'.format(ev,self.evs_data[ev]['ev_start'],self.evs_data[ev]['ev_end']))
    self._logger.info('was teleported: {}'.format(self.evs_data[ev]['was_teleported']))
    #self._logger.info('ids teleporteds: '+str(self.teleported))
    self._logger.info('crossed tls: {}'.format(self.evs_data[ev]['crossed_tls_by_ev']))
    self._logger.info('n# when ev enter: {}'.format(self.evs_data[ev]['n_when_ev_enter']))
    self._logger.info('n# when ev left: {}'.format(self.evs_data[ev]['n_when_ev_left']))
    self._logger.info('distance travelled: {}'.format(self.evs_data[ev]['distance_travelled']))

  def skip_because_json_file(self, override, skip, filename):
    if skip:
      return False

    json_name = self.__trip_path+"/"+filename+".json"
    if not override and os.path.isfile(json_name):
      self._logger.info(json_name+' exists and override='+str(override)+', skipping...')
      return True
    else:
      self._logger.info(json_name+' does not exists and override='+str(override)+', procceding...')
      return False

  def gps_to_file(self):
    df = pd.DataFrame(self.gps)
    df.to_csv('/tmp/gps.csv',index=False)


  def generate_json(self,skip, filename, evs, final_time, runtime):
    if skip:
      return

    xml_file = xml.etree.ElementTree.parse(self.__trip_file).getroot()
    tripsinfo = xml_file.findall('tripinfo')   

    data_all = {}

    data_all['param'] = []
    data_all['param'].append('{:.2f}'.format(float(1)))

    data_all['param'].append('{:.2f}'.format(float(final_time)))
    data_all['param'].append('{:.2f}'.format(float(runtime)))

    data_all['teleported'] = list(self.teleported)
    data_all['affected'] = list(self.affected_vehs)
    data_all['evs'] = self.evs

    data_all['tls'] = self.tls_active_time

    data_all['vehs'] = {}

    for veh in tripsinfo:
      veh_id = veh.attrib['id']
      data_all['vehs'][veh_id] = []

      veh_data = data_all['vehs'][veh_id]
      veh_data.append('{:.2f}'.format(float(veh.attrib['routeLength'])))
      veh_data.append('{:.2f}'.format(float(veh.attrib['duration'])))
      veh_data.append('{:.2f}'.format(float(veh.attrib['timeLoss'])))

      if veh_id in self.evs:
        veh_data.append('{:.2f}'.format(float(veh.attrib['depart'])))
        veh_data.append('{:.2f}'.format(float(veh.attrib['arrival'])))
        veh_data.append(self.evs_data[veh_id]['n_when_ev_enter'])
        veh_data.append(self.evs_data[veh_id]['n_when_ev_left'])
        veh_data.append(self.evs_data[veh_id]['tl_logics'])
        veh_data.append(self.evs_data[veh_id]['crossed_tls_by_ev'])

    data_all['stats'] = self.stats

    data_all['last_edge'] = {}
    for ev in self.evs_data:
      if self.evs_data[ev]['was_teleported']:
        data_all['last_edge'][ev] = self.evs_data[ev]['last_edge']

    file_tmp = open(self.__trip_path+"/"+filename+".json",'w+')
    file_tmp.write(json.dumps(data_all))
    file_tmp.close()    

