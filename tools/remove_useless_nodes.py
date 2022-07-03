import optparse
import os
import sys
import xml.etree.ElementTree
import multiprocessing

options = None
bounding_boxes = set()

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--osmdir", dest="osmdir", 
                        help="OSM Dir", metavar="FILE")
  opt_parser.add_option("--outputosmdir", dest="outputosmdir", 
                        help="Output OSM Dir", metavar="FILE")
  opt_parser.add_option("--zones", dest="zones", 
                        help="Zones OSM File", metavar="FILE")                                                                                                                     

  (options, args) = opt_parser.parse_args()
  return options  

def nodes_is_in_zones(allnodes,zones):
    for n in allnodes:
        for z in zones:
            if float(n[0]) >= z[0] and float(n[0]) <= z[2] and \
                float(n[1]) >= z[1] and float(n[1]) <= z[3]:
                return True

    return False

def do_work(f):
    if not os.path.isfile('{}/{}'.format(options.osmdir,f)):
        print('{}/{} is not a file!'.format(options.osmdir,f))
        return

    print('Processing {}/{}...'.format(options.osmdir,f))
    xml_file = xml.etree.ElementTree.parse('{}/{}'.format(options.osmdir,f))
    root = xml_file.getroot()

    allnodesoffile = root.findall('./node')
    allwaysoffile = root.findall('./way')
    allrelationsoffile = root.findall('./relation')

    nodes = {}
    for n in allnodesoffile:
        nodes[n.attrib['id']] = (n.attrib['lat'],n.attrib['lon'])

    ways = {}
    for w in allwaysoffile:
        ways[w.attrib['id']] = set([ nd.attrib['ref'] for nd in w.findall('./nd') ])

    relations_nodes = {}
    relations_ways = {}
    for r in allrelationsoffile:
        relations_nodes[r.attrib['id']] = set([ m.attrib['ref'] for m in r.findall('./member[@type="node"]') if m.attrib['ref'] in nodes ])
        curr_ways = (m.attrib['ref'] for m in r.findall('./member[@type="way"]') if m.attrib['ref'] in ways)
        for w in curr_ways:
            relations_nodes[r.attrib['id']] |= ways[w]
            relations_ways[r.attrib['id']] = set(curr_ways)
        

    #allinsidenodes =  get_inside_nodes(allnodesoffile,bounding_boxes)

    keep_nodes = set()
    keep_ways = set()
    keep_relations = set()

    nodes_with_highway = set([ n.attrib['id'] for n in allnodesoffile if n.find('./tag[@k="highway"]') != None ])
    ways_with_highway = set([ n.attrib['id'] for n in allwaysoffile if n.find('./tag[@k="highway"]') != None ])
    relations_with_highway = set([ n.attrib['id'] for n in allrelationsoffile if n.find('./tag[@k="highway"]') != None ])

    keep_nodes |= nodes_with_highway
    keep_ways |= ways_with_highway
    keep_relations |= relations_with_highway
    
    for way in allwaysoffile:
        if (way.attrib['id'] in ways_with_highway or \
            (way.attrib['id'] in ways and len(ways[way.attrib['id']].intersection(keep_nodes)) > 0)
            ) and \
            nodes_is_in_zones([ nodes[n] for n in nodes if n in ways[way.attrib['id']] ], bounding_boxes):
            if way.attrib['id'] in ways:
                keep_nodes |= ways[way.attrib['id']]
            keep_ways.add(way.attrib['id'])

    for relation in (allrelationsoffile):
        if (
                relation.attrib['id'] in relations_with_highway or \
                (relation.attrib['id'] in relations_nodes and len(relations_nodes[relation.attrib['id']].intersection(keep_nodes)) > 0) or \
                (relation.attrib['id'] in relations_ways and len(relations_ways[relation.attrib['id']].intersection(keep_ways)) > 0)
            ) and \
            nodes_is_in_zones([ nodes[n] for n in nodes if n in relations_nodes[relation.attrib['id']] ], bounding_boxes):
            if relation.attrib['id'] in relations_nodes:
                keep_nodes |= relations_nodes[relation.attrib['id']]
            if relation.attrib['id'] in relations_ways:
                keep_ways |= relations_ways[relation.attrib['id']]
            keep_relations.add(relation.attrib['id'])

    for node in ([ n for n in allnodesoffile if n.attrib['id'] not in keep_nodes ]):
        root.remove(node)

    for way in ([ w for w in allwaysoffile if w.attrib['id'] not in keep_ways ]):
        root.remove(way)

    for relation in ([ r for r in allrelationsoffile if r.attrib['id'] not in keep_relations ]):
        root.remove(relation)            

    print('Writing {}/{}...'.format(options.outputosmdir,f))
    xml_file.write('{}/{}'.format(options.outputosmdir,f))        

if __name__ == "__main__":
    options = get_options()

    if not os.path.isdir(options.osmdir):
        print('Error: {} is not a directory'.format(options.osmdir))
        sys.exit(1)

    if not os.path.isdir(options.outputosmdir):
        print('Error: {} is not a directory'.format(options.outputosmdir))
        sys.exit(1)

    if not os.path.isfile(options.zones):
        print('Error: {} is not a file'.format(options.zones))
        sys.exit(1)

    xml_file = xml.etree.ElementTree.parse(options.zones)
    root = xml_file.getroot()

    allinsidenodes = {}

    for n in root.findall('./node'):
        allinsidenodes[n.attrib['id']] = (n.attrib['lat'],n.attrib['lon'])

    allways = {}

    for w in (w for w in root.findall('./way') if w.find('./tag[@k="NumeroZona"]') != None ):
        allways[w.attrib['id']] = set([ nd.attrib['ref'] for nd in w.findall('./nd') ])

    for r in (r for r in root.findall('./relation') if r.find('./tag[@k="NumeroZona"]') != None):
        for m in r.findall('./member[@type="way"]'):
            allways[m.attrib['ref']] = set([ nd.attrib['ref'] for nd in w.findall('./way[@id="{}"]/nd'.format(m.attrib['ref'])) ])

    for w in allways:
        lat_min = +float("inf")
        lon_min = +float("inf")
        lat_max = -float("inf")
        lon_max = -float("inf")
        for n in allways[w]:
            lat_min = min(lat_min,float(allinsidenodes[n][0]))
            lon_min = min(lon_min,float(allinsidenodes[n][1]))
            lat_max = max(lat_max,float(allinsidenodes[n][0]))
            lon_max = max(lon_max,float(allinsidenodes[n][1]))
        bounding_boxes.add((lat_min,lon_min,lat_max,lon_max))

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count()*3)
    pool.map(do_work, os.listdir(options.osmdir))
    pool.close()
    pool.join()    
    
