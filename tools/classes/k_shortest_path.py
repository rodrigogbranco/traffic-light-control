# -*- coding: utf-8 -*-
"""
A NetworkX based implementation of Yen's algorithm for computing K-shortest paths.   
Yen's algorithm computes single-source K-shortest loopless paths for a 
graph with non-negative edge cost. For more details, see: 
http://en.m.wikipedia.org/wiki/Yen%27s_algorithm

Source code adapted to run with Python 3.8.6 and NetworkX 2.5.1 by Rodrigo Gonçalves de Branco <rodrigo.g.branco@gmail.com>
"""
__author__ = 'Guilherme Maia <guilhermemm@gmail.com>'

#__all__ = ['k_shortest_paths']

from heapq import heappush, heappop
from itertools import count

import networkx as nx
import numpy as np

class KShortestPaths():
    def k_shortest_paths(self, G, source, target, kpathsfile, k=1, weight='weight'):
        """Returns the k-shortest paths from source to target in a weighted graph G.

        Parameters
        ----------
        G : NetworkX graph

        source : node
        Starting node

        target : node
        Ending node
        
        k : integer, optional (default=1)
            The number of shortest paths to find

        weight: string, optional (default='weight')
        Edge data key corresponding to the edge weight

        Returns
        -------
        lengths, paths : lists
        Returns a tuple with two lists.
        The first list stores the length of each k-shortest path.
        The second list stores each k-shortest path.  

        Raises
        ------
        NetworkXNoPath
        If no path exists between source and target.

        Examples
        --------
        >>> G=nx.complete_graph(5)    
        >>> print(k_shortest_paths(G, 0, 4, 4))
        ([1, 2, 2, 2], [[0, 4], [0, 1, 4], [0, 2, 4], [0, 3, 4]])

        Notes
        ------
        Edge weight attributes must be numerical and non-negative.
        Distances are calculated as sums of weighted edges traversed.

        """
        if source == target:
            return ([0], [[source]]) 
        
        length, path = nx.single_source_dijkstra(G, source, weight=weight)
        if target not in length:
            raise nx.NetworkXNoPath("node %s not reachable from %s" % (source, target))

        self.write_to_file(1,length[target],path[target],kpathsfile)
        print('route 1: length={} path={}'.format(length[target],path[target]))

            
        lengths = [length[target]]
        paths = [path[target]]
        c = count()        
        B = []                        
        G_original = G.copy()    
        
        i = 1
        #for i in range(1, k):
        while i < k:
            for j in range(len(paths[-1]) - 1):            
                spur_node = paths[-1][j]
                root_path = paths[-1][:j + 1]
                
                edges_removed = []
                for c_path in paths:
                    if len(c_path) > j and root_path == c_path[:j + 1]:
                        u = c_path[j]
                        v = c_path[j + 1]
                        if G.has_edge(u, v):
                            edge_attr = G.edges[u,v]
                            G.remove_edge(u, v)
                            edges_removed.append((u, v, edge_attr))
                
                for n in range(len(root_path) - 1):
                    node = root_path[n]
                    # out-edges
                    to_remove = []
                    for u, v, edge_attr in G.out_edges(node, data=True):
                        to_remove.append((u, v))
                        #G.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))

                    for u,v in to_remove:
                        G.remove_edge(u, v)
                    
                    if G.is_directed():
                        # in-edges
                        to_remove = []
                        for u, v, edge_attr in G.in_edges(node, data=True):
                            to_remove.append((u, v))
                            #G.remove_edge(u, v)
                            edges_removed.append((u, v, edge_attr))

                        for u,v in to_remove:
                            G.remove_edge(u, v)                        
                
                spur_path_length, spur_path = nx.single_source_dijkstra(G, spur_node, weight=weight)            
                if target in spur_path and spur_path[target]:
                    total_path = root_path[:-1] + spur_path[target]
                    total_path_length = self.get_path_length(G_original, root_path, weight) + spur_path_length[target]                
                    heappush(B, (total_path_length, next(c), total_path))
                    
                for e in edges_removed:
                    u, v, edge_attr = e

                    if len(edge_attr) > 0:
                        G.add_edge(u, v, length=edge_attr['length'], weight=edge_attr['weight'])
                    else:
                        G.add_edge(u, v)


                        
            if B:
                (l, _, p) = heappop(B)
                if len(p) == len(paths[-1]) and (np.array(p) == np.array(paths[-1])).all():
                    #print('route {} is the same as route {}'.format(i+1,i))
                    continue
                else:
                    lengths.append(l)
                    paths.append(p)
                    self.write_to_file(i+1,l,p,kpathsfile)
                    print('route {}: length={} path={}'.format(i+1,l,p))
                    i += 1
            else:
                break
        
        return (lengths, paths)

    def get_path_length(self, G, path, weight='weight'):
        length = 0
        if len(path) > 1:
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                
                length += G.edges[u,v].get(weight, 1)
        
        return length

    def write_to_file(self, route, length, path, kpathsfile):
        file_tmp = open(kpathsfile,'a')
        file_tmp.write('route {}: {}'.format(route,length))
        file_tmp.write('\n')
        file_tmp.write(' '.join(path))
        file_tmp.write('\n\n')
        file_tmp.close()             
        
    #if __name__ == "__main__":
    #     G = nx.DiGraph()
    #     G.add_edge('C', 'D', length=3, weight=1)
    #     G.add_edge('C', 'E', length=2, weight=2)
    #     G.add_edge('D', 'F', length=4, weight=3)
    #     G.add_edge('E', 'D', length=1, weight=4)
    #     G.add_edge('E', 'F', length=2, weight=5)
    #     G.add_edge('E', 'G', length=3, weight=6)
    #     G.add_edge('F', 'G', length=2, weight=7)
    #     G.add_edge('F', 'H', length=1, weight=8)
    #     G.add_edge('G', 'H', length=2, weight=9)
            
        #for e in G.edges(data=True):
        #    print(e)
        
        #print()
        #print()               
    #     print(k_shortest_paths(G, 'C', 'H', 3, "length"))
        #print()
        #print() 
            
        #for e in G.edges(data=True):
        #    print(e)             
                    
        
                    
        #G=nx.complete_graph(5)
        #simple_paths = []
        #for sp in nx.all_simple_paths(G, 0, 4):
        #    simple_paths.append(sp)    
        
        #lengths, k_paths = k_shortest_paths(G, 0, 4, 2)
        
        #for sp in simple_paths:
        #    if sp not in k_paths:
        #        print('Not in k_paths: {}'.format(sp))
                
        #for kp in k_paths:
        #    if kp not in simple_paths:
        #        print('Not in simple paths {}'.format(kp))

        #print('{} {}'.format(lengths, k_paths))