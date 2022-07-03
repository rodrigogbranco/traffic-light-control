import random
import xml.etree.ElementTree
import math
import shutil

if __name__ == "__main__":
  locations = ['od']
  base_folder = '..'

  for location in locations:
    for i in range(1,6):
      total = 0
      for t in ['passenger','bus','motorcycle','emergency']:    
        path = '{0}/{1}/{1}-{2}/osm.{3}.trips.xml'.format(base_folder,location,i,t)
        xml_file = xml.etree.ElementTree.parse(path)
        root = xml_file.getroot()
        count = len(list(root.iter("trip")))
        print('{} {} {} {}'.format(location,i,t,count))
        total += count
      print('{} {} total: {}\n'.format(location,i,total))