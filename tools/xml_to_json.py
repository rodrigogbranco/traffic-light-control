import sys
import os
import xmltodict
import json

if __name__ == "__main__":
    if not os.path.isfile(sys.argv[1]):
        print("Error: {} not found".format(sys.argv[1]))
        sys.exit(1)
    
    print('Loading {}...'.format(sys.argv[1]))
    with open(sys.argv[1], 'r') as file:
        xml_content = file.read().replace('\n', '')  

    dict_data = xmltodict.parse(xml_content)

    file_tmp = open(sys.argv[2],'w+')
    file_tmp.write(json.dumps(dict_data, indent=2))
    file_tmp.close()           