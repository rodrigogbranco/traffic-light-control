import os
import sys

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
  tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
  sys.path.append(tools)
else:
  sys.exit("please declare environment variable 'SUMO_HOME'")

import sumolib
import networkx as nx
from networkx.readwrite import json_graph
import json

if __name__ == "__main__":
    file_tmp = open('{}/condensedtrimmedgraph.json'.format(os.getenv('HOME')),'r')
    origG = json_graph.node_link_graph(json.loads(file_tmp.read()))
    file_tmp.close()    

    file_tmp = open('{}/condensedtrimmedgraph.kroutes'.format(os.getenv('HOME')),'r')
    G = nx.DiGraph()
    in_route = set()
    out_route = set()
    for line in file_tmp.readlines():
        if line != '\n' and 'route' not in line:
            last = None
            for curr in line.replace('\n','').split(' '):
                if last != None:
                    edge_attr = origG.edges[last,curr]
                    G.add_edge(last,curr,title=edge_attr['title'],label=edge_attr['label'])
                    in_route.add(last)

                    if last in out_route:
                        out_route.remove(last)
                    in_route.add(curr)

                    if curr in out_route:
                        out_route.remove(curr)

                #for u, v, edge_attr in origG.out_edges(curr, data=True):
                #    if not G.has_edge(u,v):
                #        out_route.add(v)
                #        G.add_edge(u,v,title=edge_attr['title'],label=edge_attr['label'])
                last = curr
    file_tmp.close()

    src = '396396359#1'
    dst = '172433904#0'

    for n in out_route:
        for u, v, edge_attr in origG.out_edges(n, data=True):
            if v in in_route and not G.has_edge(u,v):
                G.add_edge(u,v,title=edge_attr['title'],label=edge_attr['label'])

    for n in G.nodes:
        if n == src:
            G.nodes[n]['group'] = 1
        elif n == dst:
            G.nodes[n]['group'] = 3
        elif n in in_route:
            G.nodes[n]['group'] = 2
        else:
            G.nodes[n]['group'] = 4

    file_tmp = open('{}/onlykcondensedtrimmedgraph.json'.format(os.getenv('HOME')),'w+')
    file_tmp.write(json.dumps(json_graph.node_link_data(G)))
    file_tmp.close()  