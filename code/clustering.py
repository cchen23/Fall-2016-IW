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
import skfuzzy
from sklearn import cluster

""" Returns a dataframe of cluster assignments using spectral clustering on a
given set of nodes into k clusters using affinity matrix am. """
def spectral_clustering(nodes, am, k):
    spectral = cluster.SpectralClustering(n_clusters=k, eigen_solver='arpack', affinity='cosine')
    spectral.fit(am)
    nodes = (np.reshape(nodes, (nodes.size, 1))).astype(str)
    group = spectral.labels_.astype(np.int)
    group = np.reshape(group, (group.size, 1))
    full = np.concatenate((nodes, group), axis=1)
    df = pd.DataFrame(data=full, columns=['User', 'Partition'])
    return df

""" Returns a dataframe of cluster assignments from fuzzy cmeans clustering on a
given set of nodes into c clusters. """
def fuzzy_clustering(data, c):
    m = 1
    error = 0.005
    maxiter = 1000
    cntr, u, u0, d, jm, p, fpc = skfuzzy.cluster.cmeans(data, c, m, error, maxiter, init=None, seed=None)
    print(u)
    return u

""" Returns a numpy array of in- and out-degree vectors for each user based on
a given adjacency matrix. """
def am_to_vectors(nodes, am):
    num_nodes = len(nodes)
    am = am.toarray()
    X = np.empty([num_nodes, 2 * num_nodes])
    X[: , 0 : num_nodes] = am
    X[:, num_nodes : 2 * num_nodes] = np.transpose(am);
    return X

""" Returns a symmetric matrix B = A + A'."""
def am_to_sum(am):
    am = am.toarray()
    am_sum = am + np.transpose(am)
    return am_sum

""" Returns a symmetric matrix B = A'A.https://arxiv.org/pdf/1308.0971.pdf """
def am_to_prod(am):
    am = am.toarray()
    am_prod = np.dot(am, np.transpose(am))
    return am_prod

""" Bibliometric Symmetrization.
From: ftp://ftp.cse.ohio-state.edu/pub/tech-report/2010/TR12.pdf, https://arxiv.org/pdf/1308.0971.pdf"""
def am_bib(am):
    am_bib = np.dot(am, np.transpose(am)) + np.dot(np.transpose(am), am)
    return am_bib

""" Returns a matrix of node indegrees from an adjacency matrix. """
def din_from_am(am):
    numnodes = am.shape[0]
    din_v = np.sum(am, axis=0)
    dinm = np.zeros((numnodes, numnodes))
    for i in range(numnodes):
        dinm[i][i] = din_v[i]
    print(dinm, '\n')
    return dinm

""" Returns a matrix of node outdegrees from an adjacency matrix. """
def dout_from_am(am):
    numnodes = am.shape[0]
    dout_v = np.sum(am, axis=1)
    doutm = np.zeros((numnodes, numnodes))
    for i in range(numnodes):
        doutm[i][i] = dout_v[i]
    print(doutm, '\n')
    return doutm

""" Raises diagonal entries of a square matrix to a specified power. """
def diag_power(m, power):
    numnodes = m.shape[0]
    D = np.zeros((numnodes, numnodes))
    D[np.diag_indices(numnodes)] = 1/ (m.diagonal()**power)
    return D

""" Degree Discounted Symmetrization.
From: https://arxiv.org/pdf/1308.0971.pdf ftp://ftp.cse.ohio-state.edu/pub/tech-report/2010/TR12.pdf"""
def am_deg_discounted(am):
    alpha = 0.5
    beta = 0.5
    am = am.toarray()
    dinm = din_from_am(am)
    doutm = dout_from_am(am)
    dinm_alpha = diag_power(dinm, -alpha)
    dinm_beta = diag_power(dinm, -beta)
    doutm_alpha = diag_power(doutm, -alpha)
    am_t = np.transpose(am)
    b = np.dot(np.dot(np.dot(doutm_alpha, am), np.dot(dinm_beta, am_t)), doutm_alpha)
    c = np.dot(np.dot(np.dot(dinm_beta, am_t), np.dot(doutm_alpha, am)), dinm_beta)
    a = np.add(b, c)
    return a

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
    clusters_df.to_csv('Clustering\\TEST\\Clusters\\{}.csv'.format(file_name))
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
    clusters_df.to_csv('Clustering\\TEST\\Clusters\\{}_labeled.csv'.format(file_name))
    return clusters_df

def main():
    interaction_types = ['mentions', 'replies', 'retweets']
    f = open("Clustering/TEST/Cluster_Info.csv", 'a')
    f2 = open("Clustering/TEST/Cluster_Stats.csv", 'a')
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

        # Spectral Clustering
        clusters_nums = [2, 3, 4]
        nodes = np.asarray(cmp_g.nodes())

        am_undir_weight = nx.adjacency_matrix(cmp_g.to_undirected(), weight='weight') # Undirected, weighted
        am_undir_unweight = nx.adjacency_matrix(cmp_g.to_undirected(), weight='None') # Undirected, unweighted
        am_dir_weight = nx.adjacency_matrix(cmp_g, weight='weight') # Outgoing, weighted
        am_dir_unweight = nx.adjacency_matrix(cmp_g, weight='None') # Outgoing, unweighted
        # am_dir_unweight_trans = nx.adjacency_matrix(cmp_g, weight='None').transpose() # Incoming, unweighted
        # am_dir_weight_trans = nx.adjacency_matrix(cmp_g, weight='weight').transpose() # Incoming, weighted
        # am_vectors_weight = am_to_vectors(nodes, nx.adjacency_matrix(cmp_g, weight='weight')) # Vectors of in and out degrees, weighted
        # am_vectors_unweight = am_to_vectors(nodes, nx.adjacency_matrix(cmp_g, weight='None')) # Vectors of in and out degrees, unweighted
        #
        # names = ['undirected_weighted', 'undirected_unweighted', 'outgoing_weighted', 'outgoing_unweighted', 'incoming_unweighted', 'incoming_weighted', 'vectors_weighted', 'vectors_unweighted']
        # ams = [am_undir_weight, am_undir_unweight, am_dir_weight, am_dir_unweight, am_dir_unweight_trans, am_dir_weight_trans, am_vectors_weight, am_vectors_unweight]

        am_sum_weight = am_to_sum(am_dir_weight)
        am_sum_unweight = am_to_sum(am_dir_unweight)
        am_prod_weight = am_to_prod(am_dir_weight)
        am_prod_unweight = am_to_prod(am_dir_unweight)
        am_bib_weight = am_bib(am_dir_weight)
        am_bib_unweight = am_bib(am_dir_unweight)
        am_degdiscount_weight = am_deg_discounted(am_dir_weight)
        am_degdiscount_unweight = am_deg_discounted(am_dir_unweight)

        names = ['undir_weight', 'undir_unweight', 'sum_weighted', 'sum_unweighted', 'prod_weight', 'prod_unweighted', 'bib_weight', 'bib_unweight', 'deg_discount_weight', 'deg_discount_unweight']
        ams = [am_undir_weight, am_undir_unweight, am_sum_weight, am_sum_unweight, am_prod_weight, am_prod_unweight, am_bib_weight, am_bib_unweight, am_degdiscount_weight, am_degdiscount_unweight]
        for clusters_num in clusters_nums:
            for i in range(len(names)):
                node_lists = [c_list, m_list, p_list]
                name = names[i]
                am = ams[i]
                print(name,'\n')
                print(am,'\n')
                df = spectral_clustering(nodes, am, clusters_num)
                labeled_df = add_types(df, c_list, m_list, p_list, "{}_{}clusters_{}".format(interaction_type, clusters_num, name))
                labeled_df = add_labels(df, c_df, m_df, p_df, "{}_{}clusters_{}_labels".format(interaction_type, clusters_num, name))
                part_labels = df['Partition']
                k = len(part_labels.unique())
                clusters_matrix = labeled_df
                gc.draw_color_and_shapenodes_df(cmp_g, "Clustering\\TEST\\Graphs\\spectral_{}_{}clusters_{}".format(interaction_type, k, name), interaction_type, node_lists, node_labels, k, clusters_matrix, weight='weight')

if __name__ == "__main__":
    main()
