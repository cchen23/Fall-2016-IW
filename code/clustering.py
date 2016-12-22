"""
clustering.py

Description: Clusters actors in interaction networks using various methods.
"""
import community
import csv
import graph_creator as gc
import graph_utils as util
import networkx as nx
import numpy as np
import pandas as pd
from sklearn import cluster

""" Return a dataframe of cluster assignments from spectral clustering a given
set of nodes into k clusters using affinity matrix am. """
def spectral_clustering(nodes, am, k):
    spectral = cluster.SpectralClustering(n_clusters=k, eigen_solver='arpack', affinity='cosine')
    spectral.fit(am)
    nodes = (np.reshape(nodes, (nodes.size, 1))).astype(str)
    group = spectral.labels_.astype(np.int)
    group = np.reshape(group, (group.size, 1))
    full = np.concatenate((nodes, group), axis=1)
    df = pd.DataFrame(data=full, columns=['User', 'Partition'])
    return df

""" Return a numpy array of in- and out-degree vectors for each user based on
a given adjacency matrix. """
def am_to_vectors(nodes, am):
    num_nodes = len(nodes)
    am = am.toarray()
    X = np.empty([num_nodes, 2 * num_nodes])
    X[: , 0 : num_nodes] = am
    X[:, num_nodes : 2 * num_nodes] = np.transpose(am);
    return X

""" Returns dataframe of cluster assignments using the Louvain Method of
community detection. """
def community_detection(g):
    parts = community.best_partition(g)
    df = pd.DataFrame(parts.items(), columns=['User', 'Partition'])
    dtype = {'User': str, 'Partition': str}
    for k, v in dtype.iteritems():
        df[k] = df[k].astype(v)
    return df

""" Given a dataframe of cluster assignments and lists of users in each category
returns a dataframe of cluster assignments with labels indicating each user's
category. Also saves the labeled cluster assignments to a specified csv file."""
def add_types(clusters_df, c_list, m_list, p_list, file_name):
    sLength = len(clusters_df['User'])
    clusters_df['Type'] = pd.Series(np.random.randn(sLength), index=clusters_df.index)
    for i in range(sLength):
        user = clusters_df.loc[i]['User']
        if user in c_list:
            clusters_df.loc[clusters_df['User'] == user, 'Type'] = 'c'
        elif user in p_list:
            clusters_df.loc[clusters_df['User'] == user, 'Type'] = 'p'
        elif user in m_list:
            clusters_df.loc[clusters_df['User'] == user, 'Type'] = 'm'
    clusters_df.to_csv('Clustering\\Clusters\\{}.csv'.format(file_name))
    return clusters_df

""" Given a dataframe of cluster assignments and information about each user,
returns a dataframe of cluster assignments with information about each user.
Also saves the labeled dataframe to a specified csv file. """
def add_labels(clusters_df, c_df, m_df, p_df, file_name):
    c_list = [item.lower() for item in c_df.User.values.tolist()]
    m_list = [item.lower() for item in m_df.User.values.tolist()]
    p_list = [item.lower() for item in p_df.User.values.tolist()]
    sLength = len(clusters_df['User'])
    clusters_df['Affiliation'] = pd.Series("", index=clusters_df.index)
    clusters_df['Description'] = pd.Series("", index=clusters_df.index)
    clusters_df['Followers'] = pd.Series(np.random.randn(sLength), index=clusters_df.index)
    for i in range(sLength):
        user = clusters_df.loc[i]['User']
        if user in c_list:
            index = c_df[c_df.User == user].index[0]
            clusters_df.loc[clusters_df['User'] == user, 'Followers'] = c_df.get_value(index, 'Followers') # c_df.loc[c_df['User'] == user, 'Followers']
            clusters_df.loc[clusters_df['User'] == user, 'Description'] = c_df.get_value(index, 'Description') # p_df.loc[p_df['User'] == user, 'Affiliation']
        elif user in p_list:
            index = p_df[p_df.User == user].index[0]
            clusters_df.loc[clusters_df['User'] == user, 'Followers'] = p_df.get_value(index, 'Followers') # p_df.loc[p_df['User'] == user, 'Followers']
            clusters_df.loc[clusters_df['User'] == user, 'Affiliation'] = p_df.get_value(index, 'Affiliation') # p_df.loc[p_df['User'] == user, 'Affiliation']
            clusters_df.loc[clusters_df['User'] == user, 'Description'] = p_df.get_value(index, 'Description') # p_df.loc[p_df['User'] == user, 'Affiliation']
        elif user in m_list:
            index = m_df[m_df.User == user].index[0]
            clusters_df.loc[clusters_df['User'] == user, 'Followers'] = m_df.get_value(index, 'Followers') # m_df.loc[m_df['User'] == user, 'Followers']
            clusters_df.loc[clusters_df['User'] == user, 'Description'] = m_df.get_value(index, 'Description') # p_df.loc[p_df['User'] == user, 'Affiliation']
    clusters_df.to_csv('Clustering\\Clusters\\{}_labeled.csv'.format(file_name))
    return clusters_df

def main():
    interaction_types = ['mentions', 'replies', 'retweets']
    f = open("Clustering/Cluster_Info.csv", 'a')
    f2 = open("Clustering/Cluster_Stats.csv", 'a')
    writer = csv.writer(f2, lineterminator='\n')
    writer.writerow(['Cluster Method', 'Num Clusters', 'Avg Max Percent', 'Avg Min Percent', 'Avg Conductance', 'Homogeneity Score', 'Completeness Score', 'V Score'])
    writer = csv.writer(f, lineterminator='\n')
    writer.writerow(['Cluster Method', 'Cluster Num', 'Conductance', 'Clustering Coefficient', 'Percent Celebrities', 'Percent Media', 'Percent Politicians', 'Number Celebrities', 'Number Media', 'Number Politicians'])
    f.close()
    f2.close()

    for interaction_type in interaction_types:
        edge_list = util.get_edge_list(interaction_type)
        c_list, m_list, p_list = util.get_lists()
        c_df, m_df, p_df = util.get_list_dfs()
        node_lists = [c_list, m_list, p_list]
        node_labels = ["celebrities", "media", "politicians", "others"]
        cmp_list = util.append_arrays(c_list, m_list, p_list)
        g = gc.create_graph_edge_weights(edge_list)
        cmp_g = gc.create_graph_subset(g, cmp_list)

        # Community Detection
        df = community_detection(cmp_g.to_undirected())
        labeled_df = add_types(df, c_list, m_list, p_list, "best_partition_types_{}".format(interaction_type))
        labeled_df = add_labels(df, c_df, m_df, p_df, "labels_best_partition_{}".format(interaction_type))
        part_labels = df['Partition']
        k = len(part_labels.unique())
        clusters_matrix = labeled_df
        gc.draw_color_and_shapenodes_df(cmp_g, "Clustering\\Graphs\\community_{}".format(interaction_type), interaction_type, node_lists, node_labels, k, clusters_matrix, weight='weight')

        # Spectral Clustering
        clusters_nums = [2, 3, 4]
        nodes = np.asarray(cmp_g.nodes())

        am_undir_weight = nx.adjacency_matrix(cmp_g.to_undirected(), weight='weight') # Undirected, weighted
        am_undir_unweight = nx.adjacency_matrix(cmp_g.to_undirected(), weight='None') # Undirected, unweighted
        am_dir_weight = nx.adjacency_matrix(cmp_g, weight='weight') # Outgoing, weighted
        am_dir_unweight = nx.adjacency_matrix(cmp_g, weight='None') # Outgoing, unweighted
        am_dir_unweight_trans = nx.adjacency_matrix(cmp_g, weight='None').transpose() # Incoming, unweighted
        am_dir_weight_trans = nx.adjacency_matrix(cmp_g, weight='weight').transpose() # Incoming, weighted
        am_vectors_weight = am_to_vectors(nodes, nx.adjacency_matrix(cmp_g, weight='weight')) # Vectors of in and out degrees, weighted
        am_vectors_unweight = am_to_vectors(nodes, nx.adjacency_matrix(cmp_g, weight='None')) # Vectors of in and out degrees, unweighted

        names = ['undirected_weighted', 'undirected_unweighted', 'outgoing_weighted', 'outgoing_unweighted', 'incoming_unweighted', 'incoming_weighted', 'vectors_weighted', 'vectors_unweighted']
        ams = [am_undir_weight, am_undir_unweight, am_dir_weight, am_dir_unweight, am_dir_unweight_trans, am_dir_weight_trans, am_vectors_weight, am_vectors_unweight]
        for clusters_num in clusters_nums:
            for i in range(len(names)):
                node_lists = [c_list, m_list, p_list]
                name = names[i]
                am = ams[i]
                df = spectral_clustering(nodes, am, clusters_num)
                labeled_df = add_types(df, c_list, m_list, p_list, "{}_{}clusters_{}".format(interaction_type, clusters_num, name))
                labeled_df = add_labels(df, c_df, m_df, p_df, "{}_{}clusters_{}_labels".format(interaction_type, clusters_num, name))
                part_labels = df['Partition']
                k = len(part_labels.unique())
                clusters_matrix = labeled_df
                gc.draw_color_and_shapenodes_df(cmp_g, "Clustering\\Graphs\\spectral_{}_{}clusters_{}".format(interaction_type, k, name), interaction_type, node_lists, node_labels, k, clusters_matrix, weight='weight')

if __name__ == "__main__":
    main()
