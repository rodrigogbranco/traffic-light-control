import sys
import os
import xml.etree.ElementTree
import json

if __name__ == "__main__":

    if not os.path.isfile(sys.argv[1]):
        print("Error: {} not found".format(sys.argv[1]))
        sys.exit(1)

    centro_expandido = []

    with open(sys.argv[1], 'r') as f:
        
        centro_expandido = f.read().split('\n')

    if not os.path.isfile(sys.argv[2]):
        print("Error: {} not found".format(sys.argv[2]))
        sys.exit(1)

    tmp = open(sys.argv[2],'r')        
    mapzone = json.loads(tmp.read())
    tmp.close()

    if not os.path.isfile(sys.argv[3]):
        print("Error: {} not found".format(sys.argv[3]))
        sys.exit(1)

    xml_file = xml.etree.ElementTree.parse(sys.argv[3])

    edges = set()

    for zone in centro_expandido:
        edges |= set(xml_file.find('./taz[@id="{}"]'.format(mapzone[zone])).get('edges').split(' '))
    
    tmp = open(sys.argv[4],'w+')
    tmp.write(' '.join(list(edges)))
    tmp.close()

    print('Done.')

    