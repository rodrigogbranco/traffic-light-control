import xml.etree.ElementTree
import sys
import os

if __name__ == "__main__":
  if not sys.argv[1]:
    print('Error: specifiy scenario folder')
    sys.exit(1)

  scenario = sys.argv[1]

  if not os.path.isfile('{}/osm.passenger.rou.xml'.format(sys.argv[1])):
    print('Error: could not open {}/osm.passenger.rou.xml'.format(sys.argv[1]))
    sys.exit(1)

  if not os.path.isfile('{}/../osm.net.xml'.format(sys.argv[1])):
    print('Error: could not open {}/../osm.net.xml'.format(sys.argv[1]))
    sys.exit(1)

  osm_emergency_rou = xml.etree.ElementTree.parse(scenario+'/osm.passenger.rou.xml').getroot()
  net_file = xml.etree.ElementTree.parse(scenario+'/../osm.net.xml').getroot()

  edges_with_tl = {}
  number_of_tls_x_evs = {}

  path = './connection[@tl]'

  connections = net_file.findall(path)

  ntls_set = set()

  for connection in connections:
    edge_from = connection.get('from')
    edge_to = connection.get('to')
    tl = connection.get('tl')

    if edge_from not in edges_with_tl:
      edges_with_tl[edge_from] = set()

    if edge_to not in edges_with_tl:
      edges_with_tl[edge_to] = set()

    edges_with_tl[edge_from].add(tl)
    edges_with_tl[edge_to].add(tl)

  for vehicle in osm_emergency_rou.findall('vehicle'):
    id = vehicle.attrib['id']
    my_tls = set()
    edges = vehicle.findall('route')[0].attrib['edges'].split(' ')
    for edge in edges:
      if edge in edges_with_tl:
        my_tls = my_tls.union(edges_with_tl[edge])

    tls_n = len(my_tls)

    if tls_n not in number_of_tls_x_evs:
      number_of_tls_x_evs[tls_n] = []

    number_of_tls_x_evs[tls_n].append(id)
    ntls_set.add(tls_n)

  max_tl = max(number_of_tls_x_evs)

  #for i in [5, 20, 35, 50, 65]:

  for tl in ntls_set:
    print('tls {}: {}'.format(tl,','.join(number_of_tls_x_evs[tl])))

  #print(number_of_tls_x_evs[max_tl][ int(len(number_of_tls_x_evs[max_tl])/2) ])
