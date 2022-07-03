import sys
import os
import json
from lxml import etree

if __name__ == "__main__":
    tmp = open('/tmp/routes.xml','r')
    routes = etree.parse(tmp)
    tmp.close()

    merged = []
    last_edge = None
    for route in routes.findall('//vehicle/route'):
        edges = route.attrib['edges'].split(' ')
        merged += edges[0:-1]
        last_edge = edges[-1]

    merged += [ last_edge ]

    print(' '.join(merged))