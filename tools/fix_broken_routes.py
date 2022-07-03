import networkx as nx
from networkx.readwrite import json_graph
import json
from lxml import etree
import random
import sys
import multiprocessing
from multiprocessing.pool import Pool

zone_of_edge = {}
edges_of_zone = {}
trips = []
G = None
thread_size = None
trips_size = 0

def is_valid(G,from_edge,to_edge):
    return G.has_node(from_edge) and G.has_node(to_edge) and nx.has_path(G,from_edge,to_edge)

def do_work(thread_id):
    k = thread_id
    new_trips = []
    q = 1
    while k < trips_size:
        print('processing {} of {} (tid {}) (current trips: {})...'.format(q,int(trips_size/thread_size),thread_id,len(new_trips)))
        trip = trips[k]

        edges_from_zone = edges_of_zone[zone_of_edge[trip.attrib['from']]]
        edges_to_zone = edges_of_zone[zone_of_edge[trip.attrib['to']]]

        valid = False
        if not is_valid(G,trip.attrib['from'],trip.attrib['to']):
            for i in random.sample(edges_from_zone, len(edges_from_zone)):
                for j in random.sample(edges_to_zone, len(edges_to_zone)):
                    if is_valid(G,i,j):
                        valid = True
                        trip.attrib['from'] = i
                        trip.attrib['to'] = j
                    if valid:
                        break
                if valid:
                    break
        else:
            valid = True

        if valid:
            new_trip = {}
            for attr in trip.attrib:
                new_trip[attr] = trip.attrib[attr]
            new_trips.append(new_trip)
        else:
            print('trip id {} is invalid'.format(trip.attrib['id']))

        k += thread_size
        q += 1

    return new_trips

if __name__ == "__main__":
    random.seed(42)
    file_tmp = open(sys.argv[1],'r')
    G = json_graph.node_link_graph(json.loads(file_tmp.read()))
    file_tmp.close()

    tmp = open(sys.argv[2],'r')
    districts = etree.parse(tmp)
    tmp.close() 

    for d in districts.findall('//taz'):
        edges = d.attrib['edges'].split(' ')
        for e in edges:
            zone_of_edge[e] = d.attrib['id']
        edges_of_zone[d.attrib['id']] = edges

    tmp = open(sys.argv[3],'r')
    tripfile = etree.parse(tmp)
    tmp.close()                


    trips = tripfile.findall('//trip')
    trips_size = len(trips)
    thread_size = multiprocessing.cpu_count()
    threads_id = range(0,thread_size)

    pool = Pool(processes= thread_size)
    try:
        pool_outputs = pool.map(do_work, threads_id )
    except:
        print('Error!')
        raise
    pool.close()
    pool.join()

    newroot = etree.Element("routes")

    triproot = tripfile.getroot()
    
    for att in triproot.attrib:
        newroot.attrib[att] = triproot.attrib[att]

    elements = []

    for packs in pool_outputs:
        for trip in packs:
            newtrip = etree.Element("trip")
            for attrib in trip:
                newtrip.attrib[attrib] = trip[attrib]
            elements.append(newtrip)

    elements = sorted(elements, key=lambda trip: (float(trip.attrib['depart']),trip.attrib['id']))

    for e in elements:
        newroot.append(e)

    with open(sys.argv[4],'w') as f:
        f.write(etree.tostring(newroot,pretty_print=True, encoding='utf-8', xml_declaration=True).decode("utf-8") )
