import sys
import os
from lxml import etree
import subprocess
import multiprocessing
from multiprocessing.pool import ThreadPool

global_attribs = {}

def do_work(command):
    attribs = global_attribs['attrib']
    net_file = global_attribs['net_file']
    vtype_file = global_attribs['vtype_file']

    newroot = etree.Element("routes")
    for att in attribs:
        newroot.attrib[att] = attribs[att]

    for trip in command['trips']:
        trip_el = etree.Element("trip")
        for index in command['trips'][trip]:
            trip_el.attrib[index] = command['trips'][trip][index]

        newroot.append(trip_el)

    print('Processing step {}\n'.format(command['step']))
    trip_filename = '/tmp/osm.trip-{}.xml'.format(command['step'])
    route_filename = '/tmp/osm.trip-{}.rou.xml'.format(command['step'])
    route_alt_filename = '/tmp/osm.trip-{}.rou.alt.xml'.format(command['step'])

    with open(trip_filename,'w') as f:
        f.write(etree.tostring(newroot,pretty_print=True, encoding='utf-8', xml_declaration=True).decode("utf-8") )

    proc = subprocess.Popen(['duarouter', '-n', net_file, '-r',  trip_filename, '--ignore-errors', '--begin',
                                '0', '--end', '86400', '--no-step-log', '--no-warnings', '--additional-files', vtype_file, '-v', '-o', route_filename])

    proc.wait()

    tmp = open(route_filename,'r')
    routetree = etree.parse(tmp)
    tmp.close()

    route_edges = routetree.findall('//vehicle/route')

    valid_routes = []

    for r in route_edges:
        oe = None
        de = None
        for e in r.attrib['edges'].split(' '):
            if e in global_attribs['edges']:
                if oe == None:
                    oe = e
                de = e

        if oe and de and oe != de:
            trip_id = r.getparent().attrib['id']
            command['trips'][trip_id]['from'] = oe
            command['trips'][trip_id]['to'] = de
            valid_routes.append(command['trips'][trip_id])

    os.remove(trip_filename)     
    os.remove(route_filename)
    os.remove(route_alt_filename)

    return valid_routes


if __name__ == "__main__":
    if not os.path.isfile(sys.argv[1]):
        print("Error: Edges file {} not found".format(sys.argv[1]))
        sys.exit(1)

    edges_set = set()

    print('Loading Edges from {}...'.format(sys.argv[1]))
    with open(sys.argv[1], 'r') as f:
        edges_set = set(f.read().split('\n')[0].split(' '))

    #edges_set = set(['184765909#0', '244923481', '-184765907', '37909828'])

    if not os.path.isfile(sys.argv[2]):
        print("Error: Trips file {} not found".format(sys.argv[2]))
        sys.exit(1)        

    print('Loading trips from {}...'.format(sys.argv[2]))
    tmp = open(sys.argv[2],'r')
    tree = etree.parse(tmp)
    tmp.close()

    if not os.path.isfile(sys.argv[3]):
        print("Error: Net file {} not found".format(sys.argv[3]))
        sys.exit(1)

    if not os.path.isfile(sys.argv[4]):
        print("Error: VTypes file {} not found".format(sys.argv[4]))
        sys.exit(1)

    attribs = tree.getroot().attrib
    global_attribs['attrib'] = attribs
    global_attribs['net_file'] = sys.argv[3]
    global_attribs['vtype_file'] = sys.argv[4]
    global_attribs['edges'] = edges_set
        
    commands = []
    trips_pack = {}

    count = 1
    for trip in tree.findall('//trip'):
        trip_string = {}

        for att in trip.attrib:
            trip_string[att] = trip.attrib[att]
        trips_pack[trip_string['id']] = trip_string

        if count % 5000 == 0:
            commands.append({'trips' : trips_pack, 'step' : count // 5000})
            trips_pack = {}
        count += 1

    if len(trips_pack) > 0:
        commands.append({'trips' : trips_pack, 'step' : (count // 5000) + 1})
    
    pool = ThreadPool(processes= multiprocessing.cpu_count() if multiprocessing.cpu_count() < 15 else 15)
    try:
        pool_outputs = pool.map(do_work, commands)
    except:
        print('Error!')
        raise
    pool.close()
    pool.join()    

    newroot = etree.Element("routes")
    
    for att in attribs:
        newroot.attrib[att] = attribs[att]

    elements = []

    for packs in pool_outputs:
        for trip in packs:
            trip_el = etree.Element("trip")
            for index in trip:
                trip_el.attrib[index] = trip[index]
            elements.append(trip_el)

    elements = sorted(elements, key=lambda trip: (float(trip.attrib['depart']),trip.attrib['id']))

    for e in elements:
        newroot.append(e)

    with open('/tmp/osm.restricted.trip.xml','w') as f:
        f.write(etree.tostring(newroot,pretty_print=True, encoding='utf-8', xml_declaration=True).decode("utf-8") )            



