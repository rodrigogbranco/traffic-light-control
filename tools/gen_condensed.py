import os
import networkx as nx
from networkx.readwrite import json_graph
import json
from collections import OrderedDict

def condense_recursive(G,u, exclude):
    if u in exclude:
        return

    if G.has_node(u):
        in_u = G.in_edges(u,data=True)
        out_u = G.out_edges(u,data=True)
        if len(in_u) == 1 and len(out_u) == 1:
            in_edges = next((in_t for in_t in in_u))
            out_edges = next((out_t for out_t in out_u))
            if out_edges[0] != out_edges[1]:
                G.remove_edge(in_edges[0],u)
                G.remove_edge(u,out_edges[1])
                G.remove_node(u)
                labels = OrderedDict.fromkeys(in_edges[2]['label'].split(':') + out_edges[2]['label'].split(':'))
                titles = OrderedDict.fromkeys(in_edges[2]['title'].split(':') + out_edges[2]['title'].split(':'))
                G.add_edge(in_edges[0],out_edges[1],length=in_edges[2]['length']+out_edges[2]['length'],weight=in_edges[2]['weight']+out_edges[2]['weight'],title=':'.join(list(titles)),label=':'.join(list(labels)))
                condense_recursive(G,out_edges[1],exclude)

if __name__ == "__main__":
    file_tmp = open('{}/completegraph.json'.format(os.getenv('HOME')),'r')
    G = json_graph.node_link_graph(json.loads(file_tmp.read()))
    file_tmp.close()

    exclude = ['396396359#1', '172433904#0']

    for u in list(G.nodes()):
        condense_recursive(G,u, exclude)

    file_tmp = open('{}/condensedgraph.json'.format(os.getenv('HOME')),'w+')
    file_tmp.write(json.dumps(json_graph.node_link_data(G)))
    file_tmp.close() 