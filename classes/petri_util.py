from snakes.nets import *
from classes import tpn
snakes.plugins.load([tpn,"gv"], 'snakes.nets', 'nets')
from nets import *

class PetriUtil:
  def configure(self):
    self.black_token = BlackToken()
    self.token = Value(self.black_token)
    self.inhibitor_arc = Inhibitor(self.token)

  def build_initial_block(self):
    self.pn.add_place(Place('initialplace', [self.black_token]))
    self.pn.add_transition(Transition('initialtransition'))
    self.pn.add_input('initialplace','initialtransition',self.token)    

  def build_cancelling_block(self):
    self.pn.add_place(Place('p7', []))
    self.pn.add_place(Place('pt5', [self.black_token]))
    self.pn.add_transition(Transition('t5'))

    #t5
    #artifical place
    self.pn.add_input('pt5','t5',self.token)
    self.pn.add_input('p7','t5',self.inhibitor_arc)    
    self.pn.add_output('p7', 't5', self.token)      

    print(self.pn)

  def build_places_and_transitions(self,tl_name,time_to_open_tls):
    self.pn.add_place(Place(get_place_name('t3',tl_name), [self.black_token]))

    for i in range(0,10):
      if i != 7:
        self.pn.add_place(Place(get_place_name(i,tl_name), []))

    for i in range(0,7):
      if i == 0:
        self.pn.add_transition(Transition(get_trans_name(i,tl_name), min_time=time_to_open_tls[tl_name]))
      elif i != 5:
        self.pn.add_transition(Transition(get_trans_name(i,tl_name)))

  def build_petri_net(self, conf, edges, curr_edge, time_to_open_tls):
    self.configure() 
    self.pn = PetriNet('TPN')

    self.build_initial_block()
    self.build_cancelling_block()

    for i in range(curr_edge,len(edges)):
      edge_id = edges[i]
      if edge_id in conf.edges_with_tl:
        tl_name = conf.edges[edge_id]['tl']['name']

        self.build_places_and_transitions(tl_name,time_to_open_tls)   

        self.pn.add_output(get_place_name(0,tl_name),'initialtransition',self.token)

        #global t5 links
        self.pn.add_output(get_place_name(8,tl_name),'t5',self.token)
        self.pn.add_output(get_place_name(9,tl_name),'t5',self.token)                            

        #link transitions here
        #t0
        self.pn.add_input(get_place_name(0,tl_name),get_trans_name(0,tl_name),self.token)
        self.pn.add_output(get_place_name(1,tl_name),get_trans_name(0,tl_name),self.token)
        self.pn.add_input(get_place_name(8,tl_name),get_trans_name(0,tl_name),self.inhibitor_arc)

        #t1
        self.pn.add_input(get_place_name(1,tl_name),get_trans_name(1,tl_name),self.token)
        self.pn.add_output(get_place_name(2,tl_name),get_trans_name(1,tl_name),self.token)


        #t2     
        self.pn.add_input(get_place_name(2,tl_name),get_trans_name(2,tl_name),self.token)
        self.pn.add_input(get_place_name(3,tl_name),get_trans_name(2,tl_name),self.token)
        self.pn.add_input(get_place_name(4,tl_name),get_trans_name(2,tl_name),self.inhibitor_arc)
        self.pn.add_output(get_place_name(4,tl_name),get_trans_name(2,tl_name),self.token)        

        #t3
        #artifical place
        self.pn.add_input(get_place_name('t3',tl_name),get_trans_name(3,tl_name),self.token) 

        self.pn.add_input(get_place_name(4,tl_name),get_trans_name(3,tl_name),self.inhibitor_arc)
        self.pn.add_input(get_place_name(5,tl_name),get_trans_name(3,tl_name),self.inhibitor_arc)
        self.pn.add_input(get_place_name(6,tl_name),get_trans_name(3,tl_name),self.inhibitor_arc)
        self.pn.add_input('p7',get_trans_name(3,tl_name),self.inhibitor_arc)        
        self.pn.add_input(get_place_name(8,tl_name),get_trans_name(3,tl_name),self.inhibitor_arc)

        self.pn.add_output(get_place_name(3,tl_name),get_trans_name(3,tl_name),self.token)        
        self.pn.add_output(get_place_name(6,tl_name),get_trans_name(3,tl_name),self.token)

        #t4
        self.pn.add_input(get_place_name(4,tl_name),get_trans_name(4,tl_name),self.token)
        self.pn.add_input(get_place_name(5,tl_name),get_trans_name(4,tl_name),self.inhibitor_arc)
        self.pn.add_output(get_place_name(5,tl_name),get_trans_name(4,tl_name),self.token)

        #t6
        self.pn.add_input(get_place_name(3,tl_name),get_trans_name(6,tl_name),self.inhibitor_arc)
        self.pn.add_input(get_place_name(4,tl_name),get_trans_name(6,tl_name),self.inhibitor_arc)
        self.pn.add_input(get_place_name(5,tl_name),get_trans_name(6,tl_name),self.inhibitor_arc)
        self.pn.add_input(get_place_name(9,tl_name),get_trans_name(6,tl_name),self.token)        

        self.pn.add_output(get_place_name(3,tl_name),get_trans_name(6,tl_name),self.token)

        #self.pn.draw('/home/rbranco/pn_{}.png'.format(tl_name))
        #print('pn_{}.png'.format(tl_name))      

    #self.pn.reset()
    return self.pn

def get_place_name(i,tl_name):
  return 'p{}_{}'.format(i,tl_name)

def get_trans_name(i,tl_name):
  return 't{}_{}'.format(i,tl_name)