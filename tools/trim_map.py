import sys
import os
from lxml import etree

#elements dict
edges_dict = {}
lanes_dict = {}
connections_from_dict = {}
connections_via_dict = {}
junctions_dict = {}
tls_dict = {}
roundabouts_dict = {}
requests_dict = {}

#ids dict
edges_from_dict = {}
edges_lanes_dict = {}

inside_connections = set()
inside_junctions = set()
all_junctions = set()
added_edges = set()
main_edges = set()
internal_edges = set()
inside_tls = set()
roundabouts = set()    

def add_edges_of_junction(j):
    for incLane in j.attrib['incLanes'].split(' '):
        inc_edge = '_'.join(incLane.split('_')[0:-1])
        if inc_edge not in added_edges:
            added_edges.add(inc_edge)
            edge_el = edges_dict[inc_edge]
            if 'function' not in edge_el.attrib or edge_el.attrib['function'] != 'internal':
                get_dead_junction(edge_el.attrib['from'])
            else:
                internal_edges.add(inc_edge)
        for intLane in j.attrib['intLanes'].split(' '):
            intEdge = '_'.join(intLane.split('_')[0:-1])
            if intEdge not in added_edges:
                added_edges.add(intEdge)
                internal_edges.add(intEdge)

                if intLane in junctions_dict and intLane not in all_junctions:
                    all_junctions.add(intLane)
                    add_edges_of_junction(junctions_dict[intLane])    

def get_dead_junction(j):
    if j not in inside_junctions:
        dead_junction = junctions_dict[j]
        dead_junction.attrib['type'] = 'dead_end'
        dead_junction.attrib['incLanes'] = ''
        dead_junction.attrib['intLanes'] = ''
        for r in requests_dict[j]:
            dead_junction.remove(r)
        requests_dict[j] = set()
        all_junctions.add(j)

if __name__ == "__main__":
    if not os.path.isfile(sys.argv[1]):
        print("Error: {} not found".format(sys.argv[1]))
        sys.exit(1)

    #trimmed_edges = set(['212723114', '212723119#1', '8579186#0', '212723119#3'])
    #trimmed_edges = set(['407757111#0', '407757111#1', '407757111#2', '407757111#3', '407757111#4'])
    #trimmed_edges = set(['27587518#1', '27587518#2', '27587518#3', '27587518#4'])
    
    print('Loading edges...')
    with open(sys.argv[1], 'r') as f:
        trimmed_edges = set(f.read().split(' '))

    if not os.path.isfile(sys.argv[2]):
        print("Error: {} not found".format(sys.argv[2]))
        sys.exit(1)

    print('Loading {}...'.format(sys.argv[2]))
    tmp = open(sys.argv[2],'r')
    tree = etree.parse(tmp)
    tmp.close()

    print('Loading dicts...')
    for e in tree.findall('//edge'):
        edge_id = e.attrib['id']
        edges_dict[edge_id] = e

        if 'from' in e.attrib:
            edge_from = e.attrib['from']
            if edge_from not in edges_from_dict:
                edges_from_dict[edge_from] = set()
            edges_from_dict[edge_from].add(edge_id)
        
        edges_lanes_dict[edge_id] = set()
        lanes = e.findall('./lane')
        for lane in lanes:
            lane_id = lane.attrib['id']
            edges_lanes_dict[edge_id].add(lane_id)
            lanes_dict[lane_id] = lane

    for c in tree.findall('//connection'):
        from_edge = c.attrib['from']

        if from_edge not in connections_from_dict:
            connections_from_dict[from_edge] = set()
        connections_from_dict[from_edge].add(c)

        if 'via' in c.attrib:
            connections_via_dict[c.attrib['via']] = c

    for j in tree.findall('//junction'):
        junction_id = j.attrib['id']
        junctions_dict[junction_id] = j

        requests_dict[junction_id] = set()
        for r in j.findall('./request'):
            requests_dict[junction_id].add(r)        

    for tl in tree.findall('//tlLogic'):
        tls_dict[tl.attrib['id']] = tl

    for rb in tree.findall('//roundabout'):
        rb_edges = rb.attrib['edges'].split(' ')
        for rb_edge in rb_edges:
            if rb_edge not in roundabouts_dict:
                roundabouts_dict[rb_edge] = set()
            roundabouts_dict[rb_edge].add(rb)

    print('Adding main edges, connections, junctions and TLs...')
    for e in trimmed_edges:
        if e in edges_dict:
            main_edges.add(e)
            added_edges.add(e)
            if e in connections_from_dict:
                for c in connections_from_dict[e]:
                    if c.attrib['to'] in trimmed_edges:
                        inside_connections.add(c)
                        via_edge = '_'.join(c.attrib['via'].split('_')[0:-1])
                        added_edges.add(via_edge)
                        internal_edges.add(via_edge)
                        junction = via_edge[1:]
                        junction = '_'.join(junction.split('_')[0:-1])
                        inside_junctions.add(junction)
                        all_junctions.add(junction)

                        if 'tl' in c.attrib:
                            inside_tls.add(c.attrib['tl'])

    print('Adding dead junctions of main edges...')
    for e in main_edges:
        for dest in [ dest for dest in ['from','to'] ]:
            get_dead_junction(edges_dict[e].attrib[dest])

    print('Adding internal edges of inside junctions...')
    for j in inside_junctions:
        add_edges_of_junction(junctions_dict[j])

    print('Adding incoming edges of inside junctions...')
    for j in inside_junctions:
        for incEdge in edges_from_dict[j]:
            if incEdge not in added_edges:
                added_edges.add(incEdge)
                get_dead_junction(edges_dict[incEdge].attrib['to'])

    print('Adding connections of internal edges...')
    for e in internal_edges:
        for c in connections_from_dict[e]:
            if c not in inside_connections:
                inside_connections.add(c)

        for lane in edges_lanes_dict[e]:
            c = connections_via_dict[lane]
            if c not in inside_connections:
                inside_connections.add(c)
            for dest in [ dest for dest in ['from','to'] ]:
                dest_edge = c.attrib[dest]
                if dest_edge not in added_edges:
                    added_edges.add(dest_edge)
                    get_dead_junction(dest_edge)

    print('Adding roundabouts...')
    for ed in trimmed_edges:
        if ed in roundabouts_dict:
            for rb in roundabouts_dict[ed]:
                roundabouts.add(rb)

    for rb in roundabouts:
        for ed in rb.attrib['edges'].split(' '):
            if ed not in trimmed_edges:
                added_edges.add(ed)
                for dest in [ dest for dest in ['from','to'] ]:
                    get_dead_junction(edges_dict[ed].attrib[dest])

            nodes = rb.get('nodes').split(' ')
            for node in nodes:
                if node not in inside_junctions:
                    get_dead_junction(node)

    print('Creating new file...')
    newroot = etree.Element("net")

    attribs = tree.getroot().attrib

    for att in attribs:
        newroot.attrib[att] = attribs[att]

    newroot.append(tree.find('//location'))
    for el in tree.findall('//type'):
        newroot.append(el)

    for el in added_edges:
        newroot.append(edges_dict[el])

    for el in inside_tls:
        newroot.append(tls_dict[el])          

    for el in all_junctions:
        newroot.append(junctions_dict[el])

    for el in inside_connections:
        newroot.append(el)

    for el in roundabouts:
        newroot.append(el)                              
                    
    print('Writing to {}...'.format(sys.argv[3]))
    with open(sys.argv[3],'w') as f:
        f.write(etree.tostring(newroot,pretty_print=True, encoding='utf-8', xml_declaration=True).decode("utf-8") )
    