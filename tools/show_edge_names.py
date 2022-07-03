import os
import networkx as nx
from networkx.readwrite import json_graph
import json

if __name__ == "__main__":
    file_tmp = open('{}/completegraph-allowed.json'.format(os.getenv('HOME')),'r')
    G = json_graph.node_link_graph(json.loads(file_tmp.read()))
    file_tmp.close()

    edges=['396396359#1', '419730189#1', '381723748#0', '396359616', '-145031444#3', '-145031444#2', '-145031444#1', '866223884#4', '866223884#5', '866223884#7', '866223884#8', '866223884#9', '866223884#10', '866223884#11', '866223884#12', '262851651', '262851650', '156623638', '265227050#0', '250362365#1', '265227049', '145218965#0', '145218965#3', '145218965#4', '430230832#2', '430230832#3', '430230832#4', '430230832#5', '779570618', '146133865', '-145031448#5', '146133867#0', '146133868', '146133873#0', '146133873#1', '250362361', '-146348569', '-146238118#1', '-146238118#0', '146238690#0', '156700361', '195270959', '185665960#0', '185665960#1', '263536597#0', '263536597#1', '151723428#0', '671166011#3', '671166011#4', '671166011#7', '146294291#0', '185017386#3', '146142153#0', '146142153#2', '146142153#4', '146142153#5', '146142153#6', '263721855#0', '770771717#0', '770771717#1', '770771717#3', '770771717#4', '770771717#7', '770771717#8', '770771717#9', '770771717#10', '770771717#12', '770771717#14', '-8149387#1', '260187499#0', '-475352167', '-150333735#10', '-150333735#9', '-150333735#7', '-150333735#5', '-150333735#4', '-150333735#3', '-150333735#2', '-150333735#1', '860666185', '150333747#0', '150333745', '268508777#1', '5124167#0', '5124158', '-343938395#6', '-343938395#5', '-343938395#4', '-343938395#3', '-343938395#2', '-343938395#0', '343938392#0', '343938392#1', '380373104', '462566329#0', '525242810', '380373109#0', '380373109#1', '380373112', '5124164#1', '5124164#2', '5124164#3', '212349185', '212349065', '212348456', '462566118', '212348459#0', '212348459#1', '212348459#2', '864128815#0', '864128815#1', '425383186#0', '462566123#1', '550732345', '550741745#0', '550757841#0', '550725735#0', '550725735#1', '550756710#0', '550747490', '4902378#0', '4902378#3', '810075408#1', '810075408#3', '319453543#2', '319453544', '161392067', '161392068', '161392071', '122735198', '122735128#0', '122735128#1', '122735128#2', '122735131', '463947011', '463947010', '122735129#0', '4328541', '459613590#1', '532530668#0', '532530668#1', '532530668#4', '532530664#0', '783613951', '802345235', '736243479#0', '736243479#1', '736243479#2', '95488323#0', '95488323#1', '480687747', '234367975', '366512480#0', '366512480#2', '366512480#3', '366512480#4', '366512480#5', '366512480#6', '366512480#7', '325322878#0', '325322878#1', '325322878#2', '325322878#3', '325322874#0', '325322874#2', '325322874#3', '255818925#0', '255818925#1', '255818925#2', '255818925#3', '325322859#0', '325322859#1', '325322859#2', '325322859#3', '325322859#4', '325322859#6', '325322859#7', '4584669#0', '4584669#3', '759226734', '577993222#0', '234368021', '325322846#0', '325322846#2', '325322846#3', '522151371', '27579110', '339581629', '192581475', '248870341#7', '248870341#8', '248870341#9', '325320403#0', '325320403#1', '764637917#0', '764637917#1', '764637917#2', '325320420#0', '325320420#1', '325320420#2', '325320420#3', '325320422#0', '27579054#0', '27579054#1', '577913254#0', '577913254#1', '124962743', '248870343#0', '248870343#2', '248870343#3', '248870343#4', '8547868#0', '8547868#1', '847194614#1', '27333964', '239019939#0', '22999761#0', '22999761#1', '22999761#2', '22999761#3', '22999761#4', '22999761#5', '188303695#0', '188303695#1', '239019900', '239019901#0', '239019901#2', '239019901#3', '239019901#4', '439768949', '276664815#0', '-337865808#3', '-337865808#2', '-337865808#1', '-337865808#0', '-337865806', '-462829680', '-517676964', '-324839764', '255818924#0', '255818924#1', '255818924#2', '255818924#3', '255818924#4', '255818924#5', '255818924#6', '255818924#7', '255818924#8', '255818924#11', '255818924#13', '255818924#15', '255818924#17', '183853709#0', '183853700#0', '261785598#0', '230628529#0', '183853693#0', '183853693#1', '183853693#2', '439765511', '217333504', '196799728', '776772035', '776772034', '578707887', '425930848', '425930847', '425930850#0', '38631715#0', '38631715#1', '38631715#2', '38631715#3', '14406459#1', '14406459#2', '456288159', '72921510', '38738768', '524259147#1', '172433904#0']

    last = None
    for e in edges:
        if last != None:
            x = G.edges[last,e]
            print('{} - {}'.format(x['title'],x['label']))
        last = e
