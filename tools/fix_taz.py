import sys
import os
import json
from lxml import etree

if __name__ == "__main__":

    if not os.path.isfile(sys.argv[1]):
        print("Error: Taz file {} not found".format(sys.argv[1]))
        sys.exit(1)

    if not os.path.isfile(sys.argv[2]):
        print("Error: Trips file {} not found".format(sys.argv[2]))
        sys.exit(2)               

    tmp = open(sys.argv[1],'r')
    tazfile = etree.parse(tmp)
    tmp.close()

    tazs = {}

    for taz in tazfile.findall('//taz'):
        for e in taz.attrib['edges'].split(' '):
            if e not in taz:
                tazs[e] = taz.attrib['id']
            else:
                print('edge {} in two taz: {} and {}'.format(e,tazs[e],taz.attrib['id']))

    tmp = open(sys.argv[2],'r')
    tripfile = etree.parse(tmp)
    tmp.close()                

    for trip in tripfile.findall('//trip'):
        trip.attrib['fromTaz'] = tazs[trip.attrib['from']]
        trip.attrib['toTaz'] = tazs[trip.attrib['to']]

    with open(sys.argv[3],'w') as f:
        f.write(etree.tostring(tripfile,pretty_print=True, encoding='utf-8', xml_declaration=True).decode("utf-8") )                    

        

            

    