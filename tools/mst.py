import os
import networkx as nx
from networkx.readwrite import json_graph
import json
#from networkx.algorithms import tree
#from networkx.algorithms.dag import dag_longest_path


if __name__ == "__main__":
    file_tmp = open('{}/completegraph.json'.format(os.getenv('HOME')),'r')
    G = json_graph.node_link_graph(json.loads(file_tmp.read()))
    file_tmp.close()

    routes = nx.shortest_path(G,source='172433904#0')
    maxlen = -1
    maxroute = None
    nodename = None

    for r in routes:
        length = len(routes[r])
        if length > maxlen:
            maxlen = length
            maxroute = routes[r]
            nodename = r

    print(r)
    print(maxlen)
    print(maxroute)

    #st = tree.minimum_spanning_edges(G, algorithm="prim", data=False)
    #st = tree.branchings.Edmonds(G).find_optimum()
    #print(dag_longest_path(st,weight='x',default_weight=1))