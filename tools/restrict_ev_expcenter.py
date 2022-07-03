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


    original_route = ['936519466#3', '28033948', '234368005#0', '234368005#1', '234368002', '234368009#0', '234368007#0', '248521889#0', '248521891', '917608564#0', '369915423#0', '369915423#2', '942962257#0', '942962257#2', '369907168#0', '369907168#1', '369907168#2', '27333544', '944397962#0', '944397962#1', '944454798#0', '944454798#1', '944454798#2', '124962758#0', '124962758#1', '124962758#4', '124962758#5', '124962758#7', '933373470#0', '933373470#2', '933373470#3', '933373470#4', '945523824#0', '184013930#0', '27266191#0', '27266191#1', '239019929', '239019928', '239019930#0', '239019930#1', '239019930#2', '239019930#3', '184013921', '269678074#0', '269678074#1', '269678072#0', '-701927510#1', '202867561#0', '211556998', '-938508976', '-944778228', '-27644520#6', '-27644520#2', '-27644520#1', '-370514753#2', '-370514753#1', '-946971075', '-946971074', '944778223', '230784085#1', '230784085#3', '231350452#0', '427253368#0', '629122329', '231350459#0', '231350459#1', '231350459#2', '231345867#0', '450833653#0-AddedOnRampEdge', '450833653#0', '935928222', '405498518#0', '426504889#0', '426504889#1', '426504888#1', '426505741#1', '426505740#1', '426505743#1', '426505742#1', '426505784#1', '265227060#2', '14519923#0', '196799730#0', '936875391#0', '932910494']

    oe = None
    de = None
    for e in original_route:
        if e in edges_set:
            if oe == None:
                oe = e
            de = e

    print('O: {} D: {}'.format(oe,de))