import sumolib  # noqa
import os

import xml.etree.ElementTree

if __name__ == "__main__":
    path = '/home/rodrigo/gitprojects/interscity-spres-ev-scenarios2/defined/sp/sp-5'
    #uniform
    #xml_file = xml.etree.ElementTree.parse('{}/osm.net.xml'.format('')).getroot()
    

    types = {'bus' : 4, 
             'passenger': 12, 
             'motorcycle': 4, 
             'truck': 8}

    edges = sumolib.net.readNet(os.path.join(path, 'osm.net.xml')).getEdges()

    length = {'bus' : 0, 
             'passenger': 0, 
             'motorcycle': 0, 
             'truck': 0}
             

    for edge in edges:
        for t in types:
            if edge.allows(t):
                length[t] += edge.getLaneNumber() * edge.getLength()

    for t in types:
        period = 3600 / (length[t] / 1000) / types[t]

        print('type({}) -> length({:.2f}) : p={:.2f}'.format(t,length[t],period))
