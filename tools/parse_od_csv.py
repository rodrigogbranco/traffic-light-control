import sys
import os
import json
import csv
import math

from xml.etree.ElementTree import parse, SubElement, Element, ElementTree


modetypes = { 
    4 : 'bus_bus', 5 : 'bus_bus', 6 : 'bus_bus', 7 : 'bus_bus', 8 : 'bus_bus',
    9 : 'veh_passenger', 10 : 'veh_passenger', 11 : 'veh_passenger', 12 : 'veh_passenger',
    13 : 'moto_motorcycle', 14 : 'moto_motorcycle'
}

if __name__ == "__main__":

    if not os.path.isfile(sys.argv[1]):
        print("Error: {} not found".format(sys.argv[1]))
        sys.exit(1)

    tmpfile = open(sys.argv[1],'r')
    mappings = json.loads(tmpfile.read())
    tmpfile.close()

    if not os.path.isfile(sys.argv[2]):
        print("Error: {} not found".format(sys.argv[2]))
        sys.exit(1)

    header = False

    odvalues = {}

    mintime = None

    with open(sys.argv[2]) as csvinput:
        spamreader = csv.reader(csvinput)
        for row in spamreader:
            if not header:
                header = True
            else:
                mode = int(row[117])

                if mode not in range(4,15):
                    continue

                zona_o = int(row[82])
                zona_d = int(row[86])

                if zona_d not in range(1,518):
                    continue

                if str(zona_o) not in mappings:
                    continue

                if str(zona_d) not in mappings:
                    continue                

                if modetypes[mode] not in odvalues:
                    odvalues[modetypes[mode]] = {}

                starttime = (int(row[110])*3600 + int(row[111])*60)*1000

                if mintime is None or starttime < mintime:
                    mintime = starttime

                if starttime not in odvalues[modetypes[mode]]:
                    odvalues[modetypes[mode]][starttime] = {}

                if zona_o not in odvalues[modetypes[mode]][starttime]:
                    odvalues[modetypes[mode]][starttime][zona_o] = {}

                if zona_d not in odvalues[modetypes[mode]][starttime][zona_o]:
                    odvalues[modetypes[mode]][starttime][zona_o][zona_d] = {}

                if mode not in odvalues[modetypes[mode]][starttime][zona_o][zona_d]:
                    odvalues[modetypes[mode]][starttime][zona_o][zona_d][mode] = 0                                         

                odvalues[modetypes[mode]][starttime][zona_o][zona_d][mode] += 1

    tmpfile = open(sys.argv[3],'w')
    tmpfile.write(json.dumps(odvalues))
    tmpfile.close()

    demand = Element('demand')
    tree = ElementTree(element=demand)

    for vehtype in odvalues:
        actorConfig = SubElement(demand,'actorConfig')
        actorConfig.set('id',str(vehtype))

        for starttime in odvalues[vehtype]:
            timeslice = SubElement(actorConfig,'timeSlice')
            timeslice.set('startTime',str(starttime))
            timeslice.set('duration','1000')

            for o in odvalues[vehtype][starttime]:
                for d in odvalues[vehtype][starttime][o]:
                    amount = 0
                    for mode in odvalues[vehtype][starttime][o][d]:
                        if mode in range(4,9):
                            amount += math.ceil(odvalues[vehtype][starttime][o][d][mode]/17)
                        else:
                            amount += odvalues[vehtype][starttime][o][d][mode]

                    odpair = SubElement(timeslice,'odPair')
                    odpair.set('amount',str(amount))
                    odpair.set('destination',str(mappings[str(d)]))
                    odpair.set('origin',str(mappings[str(o)]))

    tree.write(sys.argv[4])

    print('Min time: {}'.format(mintime))

