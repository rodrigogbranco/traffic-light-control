import sys
from lxml import etree

if __name__ == "__main__":
    file_tmp = open(sys.argv[1],'r')

    tmp = open(sys.argv[1],'r')
    trips = etree.parse(tmp)
    tmp.close()

    newroot = etree.Element("routes")
    triproot = trips.getroot()
    
    for att in triproot.attrib:
        newroot.attrib[att] = triproot.attrib[att]

    for trip in trips.findall('//trip'):
        if float(trip.attrib['depart']) >= float(sys.argv[2]) and float(trip.attrib['depart']) <= float(sys.argv[3]):
            newroot.append(trip)

    with open(sys.argv[4],'w') as f:
        f.write(etree.tostring(newroot,pretty_print=True, encoding='utf-8', xml_declaration=True).decode("utf-8") )
