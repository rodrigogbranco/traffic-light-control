import optparse
import sys
from xml.etree.ElementTree import parse, SubElement, Element, ElementTree
import xml.etree.ElementTree

def get_options():
  opt_parser = optparse.OptionParser()
  opt_parser.add_option("--trips", dest="trips", 
                        help="Trips File", metavar="FILE")
  opt_parser.add_option("--vehtype", type="string", dest="vehtype",
                        help="Vehicle Type")
  opt_parser.add_option("--vehclass", type="string", dest="vehclass",
                        help="Vehicle Type")
  opt_parser.add_option("--outputfile", dest="outputfile", 
                        help="Output File", metavar="FILE")                                                                         

  (options, args) = opt_parser.parse_args()
  return options                        

if __name__ == "__main__":
    options = get_options()    
    if not options.trips:
        print("Error: Trips File not provided")
        sys.exit(1)

    if not options.vehtype:
        print("Error: Vehicle type not provided")
        sys.exit(1)

    if not options.vehclass:
        print("Error: Vehicle class not provided")
        sys.exit(1)

    if not options.outputfile:
        print("Error: Output File not provided")
        sys.exit(1)        

    routes = Element('routes')
    routes.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')                     
    routes.set('xsi:noNamespaceSchemaLocation','http://sumo.dlr.de/xsd/routes_file.xsd')
    tree = ElementTree(element=routes)

    vType = SubElement(routes,'vType')
    vType.set('id',options.vehtype)
    vType.set('vClass',options.vehclass)

    tripsfile = xml.etree.ElementTree.parse(options.trips)
    root = tripsfile.getroot()

    trips_from_file = root.findall('./trip[@type="{}"]'.format(options.vehtype))

    for trip in trips_from_file:
        newtrip = SubElement(routes,'trip')
        newtrip.set('id',trip.attrib['id'])
        newtrip.set('depart',trip.attrib['depart'])
        newtrip.set('from',trip.attrib['from'])
        newtrip.set('to',trip.attrib['to'])
        newtrip.set('type',trip.attrib['type'])

        if 'fromTaz' in trip.attrib:
            newtrip.set('fromTaz',trip.attrib['fromTaz'])

        if 'toTaz' in trip.attrib:
            newtrip.set('toTaz',trip.attrib['toTaz'])
            
        newtrip.set('departLane',trip.attrib['departLane'])
        newtrip.set('departSpeed',trip.attrib['departSpeed'])

    tree.write(options.outputfile, encoding='UTF-8', xml_declaration=True)




    