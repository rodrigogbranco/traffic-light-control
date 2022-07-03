import os
import networkx as nx
from pyvis.network import Network
from networkx.readwrite import json_graph
import json
#from network2tikz import plot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

if __name__ == "__main__":
    file_tmp = open('/tmp/augmented-downtown.json','r')
    G = json_graph.node_link_graph(json.loads(file_tmp.read()))
    file_tmp.close()

    h = '1080px'
    w = '1920px'

    #h = '1920px'
    #w = '1080px'                 

    net = Network(h,w,notebook=True,directed=True)
    net.from_nx(G)
    net.show('/tmp/augmented-downtown.json-{}-{}.html'.format(h,w))
    nx.draw(G)
    plt.savefig('/tmp/augmented-downtown.json-{}-{}.pdf'.format(h,w))


    #plot(G,'{}/onlykcondensedtrimmedgraph-{}-{}.tex'.format(os.getenv('HOME'),h,w))
    #print(G.edges(data=True))          
