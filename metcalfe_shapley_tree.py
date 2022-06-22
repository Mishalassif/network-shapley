#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import networkx as nx

def metcalfe_dfs_tree(G, source, depth_limit=None):
    """Returns a dict containing each vertex and its branch and depth.
    Parameters
    ----------
    G : NetworkX graph
    source : node, required
       Specify starting node for depth-first search (the node whose Shapley value
       is being enquired)
    depth_limit : int, optional (default=len(G))
       Specify the maximum search depth
    Returns
    -------
    D : Dictionary
       dict containing each vertex and their branch and depth
    """
    
    visited = set()
    if depth_limit is None:
        depth_limit = len(G)
    
    visited.add(source)
    metcalfe_info = {node:(None, None) for node in G.nodes}
    metcalfe_info[source] = (0, 0)
    stack = [(source, 0, iter(G[source]))]
    branch_now = 1
    while stack:
            parent, depth_now, children = stack[-1]
            try:
                child = next(children)
                if child not in visited:
                    metcalfe_info[child] = (depth_now + 1, branch_now)
                    visited.add(child)
                    if depth_now < depth_limit-1:
                        stack.append((child, depth_now + 1, iter(G[child])))
            except StopIteration:
                if depth_now <= 1:
                  branch_now = branch_now + 1
                stack.pop()
    return metcalfe_info

def value(G, S, f=None):
    """Returns the Metcalfe value of a coalition in a graph.
    Parameters
    ----------
    G : NetworkX graph
    S : subset of nodes of G
    f : list of int containing vertex weights, optional (default=[1 for i in range(len(G.nodes))])

    Returns
    -------
    value : Metcalfe value of the subgraph of G induced by S
    """

    if f == None:
      f = [1 for i in range(len(G.nodes))]  
    G_S = nx.induced_subgraph(G, S)
    #nx.draw(G_S, with_labels=True, font_weight='bold')
    conn_comp_S = nx.connected_components(G_S)
    value = 0
    for comp in conn_comp_S:
        tmp = 0
        for node in comp:
          #print(node)
          tmp += f[node]  
        value += tmp*tmp
    return value

def shapley_sub_count(d_ia, d_ib, v):
    """Returns an intermediate sum in the Shapley value computation.
    Parameters
    ----------
    d_ia : distance between i and a
    d_ib : distance between i and b
    v : number of vertices

    Returns
    -------
    sum : the intermediate sum in shapley computation
    """
    k = d_ia+d_ib
    if k == 0:
        return v
    sub_count = 0.0
    for s in range(k, v):
        prod = 1
        for p in range(1, k+1):
            prod *= (s+1-p)/(v-p)
        sub_count += prod
    return sub_count
    
def shapley(G, i, f=None):
    """Returns the Shapley value of a node in a graph.
    Parameters
    ----------
    G : NetworkX graph
    i : node of G
    f : list of int containing vertex weights, optional (default=[1 for i in range(len(G.nodes))])

    Returns
    -------
    shapley : Shapley value of node i
    """
    
    if f == None:
      f = [1 for i in range(len(G.nodes))]
    shapley = 0.0
    branch_dist = metcalfe_dfs_tree(G, i)
    for a in G.nodes:
        if branch_dist[a][1] == None:
          continue
        for b in G.nodes:
            if branch_dist[b][1] == None:
              continue
            if branch_dist[a][1] != branch_dist[b][1] or (a == b and a == i):
                shapley += f[a]*f[b]*shapley_sub_count(branch_dist[a][0], branch_dist[b][0], len(G.nodes))
    return shapley/len(G.nodes)
