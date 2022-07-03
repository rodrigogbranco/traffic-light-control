from networkx.readwrite import json_graph
import json
from classes.k_shortest_path import KShortestPaths
import os
import sys

if __name__ == "__main__":
    file_tmp = open('{}/{}'.format(os.getenv('HOME'),sys.argv[4]),'r')
    G = json_graph.node_link_graph(json.loads(file_tmp.read()))
    file_tmp.close()
    #print(G.edges(data=True))

    alg = KShortestPaths()

    kpathsfile = '{}/{}'.format(os.getenv('HOME'),sys.argv[5])

    file_tmp = open(kpathsfile,'w+')
    file_tmp.close()
    ret  = alg.k_shortest_paths(G, sys.argv[1], sys.argv[2], kpathsfile, int(sys.argv[3]), weight='weight')

    #print("Done: {}".format(str(ret)))

