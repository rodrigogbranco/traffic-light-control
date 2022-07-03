import os
import networkx as nx
from networkx.readwrite import json_graph
import json

if __name__ == "__main__":
    file_tmp = open('{}/completegraph-allowed.json'.format(os.getenv('HOME')),'r')
    G = json_graph.node_link_graph(json.loads(file_tmp.read()))
    file_tmp.close()

    nodes = ['8148325','-416161227','416161227','14408823','27670210','866562098','126052480','15967012','440744039','4685095#0', '163760397', '159114536', '438155977', '151255824', '161392068']

    src = '396396359#1'
    target='172433904#0'

    print('Até as pontes:\n')
    #for n in nodes_to_check:
    n = nodes[-1]
    l, p = nx.single_source_dijkstra(G, source=src, target=n)
    print('n={} {} {}'.format(n,l,p))
    print('De {} até {}'.format(n,target))
    l, p = nx.single_source_dijkstra(G, source=n, target=target)
    print('\t{} {}\n'.format(l,p))

    for n in nodes:
        G.remove_node(n)

    length, path = nx.single_source_dijkstra(G, source=src, target=target)
    print('Menor caminho de {} até {} sem nós-ponte: {} {}'.format(src,target,length,path))        


    #for n in nodes:
    #print('{} {}'.format(length,path))

    #minlen = 10000
    #minroute = None
    #nodename = None

    #for n in nodes:
    #    if n in path:
    #        length = len(path[n])
    #        if length < minlen:
    #            minlen = length
    #            minroute = path[n]
    #            nodename = n

    #print(nodename)
    #print(minlen)
    #print(minroute)
