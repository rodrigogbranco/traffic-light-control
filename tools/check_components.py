import networkx as nx
from networkx.readwrite import json_graph
import json
import sys

if __name__ == "__main__":
    file_tmp = open(sys.argv[1],'r')
    G = json_graph.node_link_graph(json.loads(file_tmp.read()))
    file_tmp.close()

    #largest_cc = max(nx.connected_components(G), key=len)

    x = [
        (len(c),c)
        for c in sorted(nx.weakly_connected_components(G), key=len, reverse=True)
    ]

    for i in range(1,len(x)):
        print(x[i][1])