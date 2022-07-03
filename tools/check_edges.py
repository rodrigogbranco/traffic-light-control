import sumolib

if __name__ == "__main__":

    types = set(['passenger', 'motorcycle', 'bus', 'emergency'])

    ignore = set(['highway.service','highway.steps','highway.cycleway','highway.pedestrian','highway.subway','railway.subway',
              'highway.footway','railway.rail','railway.path','highway.path'])

    allowed = {
        'highway.living_street' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.motorway' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.motorway_link' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.primary' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.primary_link' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.residential' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.secondary' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.secondary_link' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.tertiary' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.tertiary_link' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.track' :  set(['motorcycle']),
        'highway.trunk' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.trunk_link' :  set(['passenger', 'motorcycle', 'bus', 'emergency']),
        'highway.unclassified' :  set(['passenger', 'motorcycle', 'bus', 'emergency'])
    }

    edges = sumolib.net.readNet('/mnt/c/Users/rodri/Documents/linux/odreal/osm.net.xml').getEdges()

    #edges = sumolib.net.readNet('/mnt/c/Users/rodri/Documents/linux/interscity-spres-ev-scenarios2/defined/sp/osm.net.xml').getEdges()

    for e in edges:
        for t in types:
            et = e.getType()
            if et not in ignore and t in allowed[et] and not e.allows(t):
                print('t={} e={} mismatch'.format(t,e))