import xml.etree.ElementTree
import random

if __name__ == "__main__":
    #random.seed(314)
    net = xml.etree.ElementTree.parse('/home/rodrigobranco/odreal/osm.net.xml')
    root = net.getroot()

    print(random.choice([ e.attrib['id'] for e in root.findall('./edge[@type="highway.primary"]') ]))
