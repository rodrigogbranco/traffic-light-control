import os
import networkx as nx
from networkx.readwrite import json_graph
import json
#from networkx.algorithms import tree
#from networkx.algorithms.dag import dag_longest_path

def add_recursive(oldGraph,newGraph,node,depth):
    if depth <= 0:
        return

    if not oldGraph.has_node(node):
        return
    
    adjs = oldGraph.out_edges(node, data=True)
    for u, v, edge_attr in adjs:
        if not newGraph.has_edge(u, v):
            newGraph.add_edge(u, v, length=edge_attr['length'], weight=edge_attr['weight'], title=edge_attr['title'], label=edge_attr['label'])
            add_recursive(oldGraph,newGraph,v,depth-1)

    adjs = oldGraph.in_edges(node, data=True)
    for v, u, edge_attr in adjs:
        if not newGraph.has_edge(v, u):
            newGraph.add_edge(v, u, length=edge_attr['length'], weight=edge_attr['weight'], title=edge_attr['title'], label=edge_attr['label'])
            add_recursive(oldGraph,newGraph,v,depth-1)

if __name__ == "__main__":
    file_tmp = open('{}/condensedgraph.json'.format(os.getenv('HOME')),'r')
    G = json_graph.node_link_graph(json.loads(file_tmp.read()))
    file_tmp.close()

    route = "396396359#1 396360052 396392015 396396148 260203865#0 410114826 410114825#0 -396824705#1 -519409036 -519409038 -246510535#1 -437061991 437060902#0 246510542 410116366#0 410116366#1 146197211#0 146197211#3 146197211#4 146197211#5 146197211#8 146197211#9 436048721#0 436048721#1 228042734 262851666 228064530#2 228064530#3 228064530#4 228064530#5 4769567 337873120#0 337873120#1 337873120#2 337873120#3 337873120#4 337873120#5 396480841 396481179 185675276#1 185675276#2 185675276#3 185675276#4 185144058#0 185144058#1 185144058#2 185144058#3 185144058#4 185144058#5 185144058#6 27427193#1 27427193#2 27427193#3 27427193#4 27427193#5 27427193#6 151766145#0 185148898 8451671#0 8451671#5 14408823 480196895 866807552#1 124962799 338548192 124962800 257344683 202867536 701927509#0 211556998 -27644520#6 -27644520#5 -27644520#4 -27644520#1 -27644520#0 -370514753#1 -370514753#0 -230784086#2 231350481#0 231350481#2 231350481#3 231350473#0 231350473#1 14520867 231350478#2 231355586#0 231355585#0 231355585#4 231355593#0 231355593#1 38630340 38630328#0 38630639#0 236120862#0 236120862#1 425929169#0 425929169#1 425929169#2 425929169#4 425929172#0 38631715#3 14406459#1 14406459#2 456288159 72921510 38738768 524259147#1 172433904#0"

    route_set = set()
    for r in route.split(' '):
        route_set.add(r)
    
    trimmedG = nx.DiGraph()
    maxdepth = 20

    for u in route_set:
        add_recursive(G,trimmedG,u,maxdepth)

    file_tmp = open('{}/condensedtrimmedgraph.json'.format(os.getenv('HOME')),'w+')
    file_tmp.write(json.dumps(json_graph.node_link_data(trimmedG)))
    file_tmp.close()