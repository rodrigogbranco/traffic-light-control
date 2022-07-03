from logger import Logger
import requests
import sys

class SpresEVUtil():
    def __init__(self, prefix, tag):
      self._tag = tag
      self._prefix = prefix
      self._logger = Logger(self.__class__.__name__).get()      

    def createOrUpdate(self, ev):
      r = requests.post('http://spres-ev:6078/emergency_vehicles', 
        json={
          'emergency_vehicle' : {
            'rfid' : self.makePrefix(ev),
            'ev_type' : 'Ambulance',
            'obs' : 'EV ' + self.makePrefix(ev)
          }
        }
      )
      return r.status_code == 200

    def registerFakeTrafficLight(self):
      r = requests.get('http://spres-ev:6078/fake_traffic_light/register',
        json={
          'fake_traffic_light' : {
            'url' : 'http://docker-sumo:7000'
          }
        }
      )
      self._fakeTLUUID = r.content


    def notify(self, ev_id, tls_ids, mustNotifySet):
      if len(mustNotifySet) > 0:
        r = requests.get('http://spres-ev:6078/fake_traffic_light/notify',
          json={
            'uuid'   : self._fakeTLUUID,
            'tls_id' : list(mustNotifySet),
            'ev'     : self.makePrefix(ev_id),
            'command': 'authorize',
            'tag' : self._tag
          }
        )
        self._logger.debug(r.content)
        # sys.exit(0)

    def doMore(self):
        pass

    def makePrefix(self, value):
      return self._prefix + '-' + value

