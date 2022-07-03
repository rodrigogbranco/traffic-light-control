import sys
import os
import json
from lxml import etree

if __name__ == "__main__":
    edges_str  = '572744596#0 572744596#1 535658884#0 22876414#0 22876414#1 22876414#2 22876414#3 22954833#1 111549929#4 111549929#5 111549929#6 -133203518#7 -133203518#6 -133203518#5 22876517#0 22876517#1 22876517#2 22954833#5 572744590#4 572744590#5 572744590#6 -133203518#3 -133203518#2 -133203518#1 22897032#0 22954833#12 22954833#13 572744532#2 572744532#2.108 572744549#0 572744549#1 -111604743 -233249442#1 -233249442#0 305638173#0 305638173#1 572740898 572744537#0 572744537#1 572744537#2 572744537#3 572744492#0 572744492#1 572744492#6 572744492#8 22906913#3 22906913#4 22906913#5 22906913#6 22906913#7 22906913#8 22906913#9 22906913#10 22906913#11 22906913#12 22906913#13 133198389#0 133198389#1 22981878#0 22981878#2 22981878#3 22981878#4 127878554#0 127878554#1 127878554#2 127878554#3 572744495#0 572744495#1 38321122#0 38321122#1 38321122#2 38321122#3 38321122#4 38321122#5 383741243#0 383741243#1 383741243#2 383741243#3 383741243#4 101186592#0'

    edges = edges_str.strip().split(' ')

    attr_qname = etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'noNamespaceSchemaLocation')            

    routes = etree.Element("routes",
                    {attr_qname: 'http://sumo.dlr.de/xsd/routes_file.xsd'},
                    nsmap={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

    for i in range(1,len(edges)):
        trip = etree.Element("trip")

        trip.attrib['depart'] = '25200.00'
        trip.attrib['departLane'] = 'free'
        trip.attrib['departSpeed'] = 'max'
        trip.attrib['type'] = 'ev_passenger'

        trip.attrib['id'] = 'vehevx{}'.format(i)
        trip.attrib['from'] = edges[i-1]
        trip.attrib['to'] = edges[i]

        routes.append(trip) 

    with open('/tmp/trips.xml','w') as f:
        f.write(etree.tostring(routes,pretty_print=True, encoding='utf-8', xml_declaration=True).decode("utf-8") )    