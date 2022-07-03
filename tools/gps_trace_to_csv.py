import pandas as pd
import xmltodict

if __name__ == "__main__":
    with open('/home/rodrigo/augmented-downtown/gps-delimter.gpx','r') as file:
        xml_content = file.read().replace('\n', '')  

    dict_data = xmltodict.parse(xml_content)

    gps_csv = {'scenario' : [], 'ev' : [], 'step' : [], 'lon' : [], 'lat' : []}

    count = 1
    for r in dict_data['gpx']['trk']['trkseg']['trkpt']:
        gps_csv['scenario'].append('augmented')
        gps_csv['ev'].append('expanded-center')
        gps_csv['step'].append(count)
        gps_csv['lon'].append(r['@lon'])
        gps_csv['lat'].append(r['@lat'])
        count += 1

    df = pd.DataFrame(gps_csv)
    df.to_csv('/tmp/gps4.csv',index=False)  