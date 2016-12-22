"""
conductance.py

Description: Computes conductance of clusters
"""
import clustering
import graph_creator as gc
import graph_utils as util
import networkx as nx
import networkx_cuts as nxcuts
import numpy as np

""" Return conductance of a specified cluster in a given clustering of a
network. """
def conductance_score(g, cluster_df, partition, weight=None):
    cluster_rows = cluster_df.loc[cluster_df['Partition'] == partition]
    cluster_nodes = cluster_rows.User
    conductance_score = nxcuts.conductance(g, cluster_nodes, weight=weight)
    return conductance_score

def test_conductance():
    edge_list = util.get_edge_list('replies')
    c_list, m_list, p_list = util.get_lists()
    c_df, m_df, p_df = util.get_list_dfs()
    node_lists = [c_list, m_list, p_list]
    node_labels = ["celebrities", "media", "politicians", "others"]
    cmp_list = util.append_arrays(c_list, m_list, p_list)
    g = gc.create_graph_edge_weights(edge_list)
    cmp_g = gc.create_graph_subset(g, cmp_list)
    nodes = np.asarray(cmp_g.nodes())
    node_lists = [c_list, m_list, p_list]
    am = clustering.am_to_vectors(nodes, nx.adjacency_matrix(cmp_g, weight='None')) # Vectors of in and out degrees, unweighted
    clusters_df = clustering.spectral_clustering(nodes, am, 3)

    for i in range(3):
        conductance = conductance_score(cmp_g, clusters_df, str(i))
        print(conductance)

def main():
    test_conductance()

if __name__ == "__main__":
    main()
