import sys
import os
import xml.etree.ElementTree
import json

if __name__ == "__main__":

    if not os.path.isfile(sys.argv[1]):
        print("Error: {} not found".format(sys.argv[1]))
        sys.exit(1)

    mapping = {}

    xml_file = xml.etree.ElementTree.parse(sys.argv[1])
    for way in (xml_file.findall('way')):
        nzona = way.find('./tag[@k="NumeroZona"]')
        
        if nzona == None:
            print('way {} does not have tag'.format(way.attrib['id']))
            continue

        mapping[nzona.attrib['v']] = way.attrib['id']

    ofile = open(sys.argv[2],'w')
    ofile.write(json.dumps(mapping))
    ofile.close()

    print('Done.')

    