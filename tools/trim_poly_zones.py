import sys
import os
import json
from lxml import etree

if __name__ == "__main__":

    original_folder = '/home/rodrigo/metro-od-2017'
    dest_dir = '/home/rodrigo/augmented-downtown'             

    tmp = open('{}/centro-expandido.txt'.format(original_folder), 'r')
    zones = set(tmp.read().split(' '))
    tmp.close()

    tmp = open('{}/mapzone.json'.format(original_folder), 'r')
    original_mapzone = json.loads(tmp.read())
    tmp.close() 

    trim_zones = {}

    taz_ids = set()

    for z in zones:
        trim_zones[z] =  original_mapzone[z]
        taz_ids.add(trim_zones[z])

    file_tmp = open('{}/mapzone.json'.format(dest_dir), 'w')
    file_tmp.write(json.dumps(trim_zones))
    file_tmp.close()

    tmp = open('{}/zones.osm.poly.xml'.format(original_folder),'r')
    poly = etree.parse(tmp)
    tmp.close()

    for el in poly.findall('//poly'):
        if el.attrib['id'] not in taz_ids:
            poly.getroot().remove(el)

    with open('{}/zones.osm.poly.xml'.format(dest_dir),'w') as f:
        f.write(etree.tostring(poly,pretty_print=True, encoding='utf-8', xml_declaration=True).decode("utf-8") )

    tmp = open('{}/districts.taz.osm.xml'.format(original_folder),'r')
    taz = etree.parse(tmp)
    tmp.close() 

    for el in taz.findall('//taz'):
        if el.attrib['id'] not in taz_ids:
            taz.getroot().remove(el)   

    with open('{}/districts.taz.osm.xml'.format(dest_dir),'w') as f:
        f.write(etree.tostring(taz,pretty_print=True, encoding='utf-8', xml_declaration=True).decode("utf-8") )                    

        

            

    