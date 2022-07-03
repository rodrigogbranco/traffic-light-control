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
    G = nx.DiGraph()
    edges = sumolib.net.readNet('{}/osm.net.xml'.format(sys.argv[1])).getEdges()

    for e in edges:
        for c in e.getIncoming():
            G.add_edge(c.getID(), e.getID(), length=c.getLength(), weight=c.getLength(), name=e.getName())

        for c in e.getOutgoing():
            G.add_edge(e.getID(), c.getID(), length=e.getLength(), weight=e.getLength(), name=e.getName())

    file_tmp = open('{}/graphwithname.json'.format(os.getenv('HOME')),'w+')
    file_tmp.write(json.dumps(json_graph.node_link_data(G)))
    file_tmp.close()

    #print(G.edges(data=True))        