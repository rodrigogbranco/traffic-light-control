from xml.etree.ElementTree import parse, SubElement
import xml.etree.ElementTree
import os
import sys

if __name__ == "__main__":
    if not os.path.isfile(sys.argv[1]):
        print("Error: {} not found".format(sys.argv[1]))
        sys.exit(1)

    ifile = parse(sys.argv[1])

    for way in (ifile.findall('way')):
        nzona = way.find('./tag[@k="NumeroZona"]')
        if nzona == None:
            print('way {} does not have tag'.format(way.attrib['id']))
            continue
        else:
            print('{} {}'.format(way.attrib['id'],nzona.attrib['v']))
        
        tag = SubElement(way,'tag')
        tag.set('k', 'boundary')
        tag.set('v', 'administrative')

    ifile.write(sys.argv[2])
