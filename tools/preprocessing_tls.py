import os
import sys

from lxml import etree
import json


if __name__ == "__main__":
    print('reading from {}/osm.net.xml...'.format(sys.argv[1]))
    tmp = open('{}/osm.net.xml'.format(sys.argv[1]), 'r')
    net_file = etree.parse(tmp)
    tmp.close()

    tls = {}

    for c in  net_file.findall('//connection[@tl]'):
        from_edge = c.attrib['from']
        to_edge = c.attrib['to']

        if from_edge not in tls:
            tls[from_edge] = {}
            tls[from_edge]['edges'] = {}
            tls[from_edge]['in'] = set()

        if to_edge not in tls[from_edge]['edges']:
            tls[from_edge]['edges'][to_edge] = { 'tl': c.attrib['tl'], 'index': set()}

        tls[from_edge]['edges'][to_edge]['index'].add(c.attrib['linkIndex'])

    for inEdge in tls:
        for outEdge in tls[inEdge]['edges']:
            tls[inEdge]['edges'][outEdge]['index'] = list(tls[inEdge]['edges'][outEdge]['index'])

            if outEdge in tls:
                tls[outEdge]['in'].add(inEdge)

    for edge in tls:
        tls[edge]['in'] = list(tls[edge]['in'])
        
    print('writing to {}/osm.tls.json...'.format(sys.argv[1]))
    file_tmp = open('{}/osm.tls.json'.format(sys.argv[1]),'w+')
    file_tmp.write(json.dumps(tls))
    file_tmp.close()