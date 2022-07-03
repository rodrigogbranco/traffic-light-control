import pandas as pd
from lxml import etree

if __name__ == "__main__":
    tmp = open('/home/rodrigo/metro-od-2017/zones.osm.xml','r')
    osmfile = etree.parse(tmp)
    tmp.close()  

    gps_csv = {'scenario' : [], 'ev' : [], 'step' : [], 'lon' : [], 'lat' : [], 'Area_ha_2': [], 'NomeDistrito_Municipio' : [], 'NomeMunicipio' : [], 'NomeZona' : [],
                'NumDistrito_Municipio' : [], 'NumeroMunicipio' : []}

    nodes = {}
    for node in osmfile.findall('//node'):
        nodes[node.attrib['id']] = {'lat' : node.attrib['lat'], 'lon' : node.attrib['lon']}
 
    for relation in osmfile.findall('//way'):
        item = {}
        for tag in relation.findall('./tag'):
            item[tag.attrib['k']] = tag.attrib['v']

        if 'NumeroZona' in item:
            for step,node in enumerate([ nd.attrib['ref']  for nd in relation.findall('./nd')]):
                if node in nodes:
                    gps_csv['scenario'].append('metro2017')
                    gps_csv['ev'].append(item['NumeroZona'])
                    gps_csv['step'].append(step+1)
                    gps_csv['lon'].append(nodes[node]['lon'])
                    gps_csv['lat'].append(nodes[node]['lat'])
                    gps_csv['Area_ha_2'].append(item['Area_ha_2'])
                    gps_csv['NomeDistrito_Municipio'].append(item['NomeDistrito_Municipio'])
                    gps_csv['NomeMunicipio'].append(item['NomeMunicipio'])
                    gps_csv['NomeZona'].append(item['NomeZona'])
                    gps_csv['NumDistrito_Municipio'].append(item['NumDistrito_Municipio'])
                    gps_csv['NumeroMunicipio'].append(item['NumeroMunicipio'])

    df = pd.DataFrame(gps_csv)
    df.to_csv('/home/rodrigo/charts/smartcity-tpn/metro2017-gps.csv',index=False)  