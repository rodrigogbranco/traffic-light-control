import random
import xml.etree.ElementTree
import math
import shutil

if __name__ == "__main__":
  locations = ['od']
  base_folder = '/mnt/c/Users/rodri/Documents/linux'

  evs = {'od': ['vehev1', 'vehev2', 'vehev3']
  }

  veh_types = ['passenger', 'bus', 'motorcycle']        

  #random.seed(43)

  for location in locations:
    print(location) 

    #partial_data = get_data('new-{}-scenarios-size.ods'.format(location))
    
    for i in range(4,0,-1):
      scenario_higher = '{}/{}/{}-{}'.format(base_folder,location,location,i+1)
      scenario_folder = '{}/{}/{}-{}'.format(base_folder,location,location,i)

      shutil.copytree(scenario_higher,scenario_folder)

      for v in veh_types:
        print(v)
        print(i)

        xml_file = xml.etree.ElementTree.parse('{}/osm.{}.trips.xml'.format(scenario_higher,v))
        root = xml_file.getroot()
        els = [ el.attrib['id'] for el in xml_file.findall('trip') if el.attrib['id'] not in evs[location] ]
        remove_els = random.sample(els,int(len(els)*0.25))        

        xml_file = xml.etree.ElementTree.parse('{}/osm.{}.trips.xml'.format(scenario_folder,v))
        root = xml_file.getroot()
        for el in [ el for el in xml_file.findall('trip') if el.attrib['id'] in remove_els]:
          root.remove(el)
        xml_file.write('{}/osm.{}.trips.xml'.format(scenario_folder,v))


        xml_file = xml.etree.ElementTree.parse('{}/osm.{}.rou.xml'.format(scenario_folder,v))
        root = xml_file.getroot()
        for el in [ el for el in xml_file.findall('vehicle') if el.attrib['id'] in remove_els ]:
          root.remove(el)
        xml_file.write('{}/osm.{}.rou.xml'.format(scenario_folder,v))

        xml_file = xml.etree.ElementTree.parse('{}/osm.{}.rou.alt.xml'.format(scenario_folder,v))
        root = xml_file.getroot()
        for el in [ el for el in xml_file.findall('vehicle') if el.attrib['id'] in remove_els ]:
          root.remove(el)
        xml_file.write('{}/osm.{}.rou.alt.xml'.format(scenario_folder,v))        


      



