import random
import xml.etree.ElementTree
from pyexcel_ods3 import get_data # noqa
import math
import shutil

if __name__ == "__main__":
  fromlocation = 'sp'
  tolocation = 'spbi'

  override = False
  

  from_folder = '../interscity-spres-ev-scenarios3/{0}/{0}-5'.format(fromlocation)
  to_folder = '../interscity-spres-ev-scenarios3/{}'.format(tolocation)

  ev = 'vehev'

  files = {'trips' : 'trip', 'rou': 'vehicle', 'rou.alt': 'vehicle'}
  elements = {'trips' : '', 'rou': '', 'rou.alt': ''}

  for f in files:
    xml_file = xml.etree.ElementTree.parse('{}/osm.emergency.{}.xml'.format(from_folder,f))
    root = xml_file.getroot()
    element = root.find('./{}[@id="{}"]'.format(files[f],ev))
    elements[f] = element


  for i in range(1,6):
    print(i)
    for f in files:
      path = '{}/{}-{}/osm.emergency.{}.xml'.format(to_folder,tolocation,i,f)
      xml_file = xml.etree.ElementTree.parse(path)
      root = xml_file.getroot()

      if override or root.find('./{}[@id="{}"]'.format(files[f],ev)) is None:
        root.insert(1,elements[f])
        print('{} was inserted in {}'.format(ev,path))
      else:
        print('Could not insert {} in {}'.format(ev,path))

      xml_file.write(path)


      



