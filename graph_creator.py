"""
graph_creator.py

Description: Creates graphs with interactions as edges and users as nodes.
"""
import csv
import graph_utils_sql as util
import networkx as nx
import numpy as np
import pandas as pd
import pylab as plt
import sys
import degree_vectors as vec
import clustering as c
import sklearn.metrics.cluster as cluster

""" Returns a graph created from a random subset of edges from an edge list. p
denotes the proportion of edges that are included. """
def get_rand_subset(edge_list, p):
    edge_subset = edge_list.sample(frac=p, axis=0)
    return edge_subset

""" Returns a directed graph from an edge list, with edges weighted according to
the number of interactions between two nodes. """
def create_graph_edge_weights(edge_list):
    default_weight = 1
    G = nx.DiGraph()
    num_edges = edge_list.shape[0]
    for i in range(num_edges):
        n0 = edge_list.loc[i, 'start_node']
        n1 = edge_list.loc[i, 'end_node']
        # Don't include self-referencing edges
        if n0 == n1:
            continue
        if G.has_edge(n0,n1):
            G[n0][n1]['weight'] += default_weight
        else:
            G.add_edge(n0,n1, weight=default_weight)
    return G

""" Returns an undirected graph from an edge list, with edges weighted according
to the number of interactions between two nodes. """
def create_undirected_graph_edge_weights(edge_list):
    default_weight = 1
    G = nx.Graph()
    edge_list.end_node = edge_list.end_node.str.encode('utf-8')
    for i in range(len(edge_list.index)):
        n0 = edge_list['start_node'].iloc[i]
        n1 = edge_list['end_node'].iloc[i]
        # Don't include self-referencing edges
        if n0 == n1:
            continue
        if G.has_edge(n0,n1):
            G[n0][n1]['weight'] += default_weight
        else:
            G.add_edge(n0,n1, weight=default_weight)
    return G

""" Returns a subset of a given graph's nodes, including only the ones with a
minimum indegree."""
def filter_indegree(g, min_degree):
    indeg = g.in_degree()
    to_keep = [n for n in indeg if indeg[n] >= min_degree]
    return to_keep

""" Draws an interaction graph with nodes colored according to user category. """
def draw_color_nodes(G, out_file, interaction_type):
    plt.clf()
    print("getting layout")
    pos = nx.spring_layout(G)
    nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.3, arrows=True)
    nodes = set(G.nodes())

    print("drawing c_list")
    c_nodes = list(set(c_list).intersection(nodes))
    nx.draw_networkx_nodes(G,pos, nodelist=c_nodes, node_color='r', node_size=15,label='celebrity')

    print("drawing m_list")
    m_nodes = list(set(m_list).intersection(nodes))
    nx.draw_networkx_nodes(G,pos, nodelist=m_nodes, node_color='g', node_size=15,label='media')

    print("drawing p_list")
    p_nodes = list(set(p_list).intersection(nodes))
    nx.draw_networkx_nodes(G,pos, nodelist=p_nodes, node_color='b', node_size=15,label='politician')

    print("drawing others")
    other_nodes = nodes - set(c_list) - set(m_list) - set(p_list)
    o_nodes = list(other_nodes)
    nx.draw_networkx_nodes(G,pos, nodelist=o_nodes, node_color='k', node_size=15,label='other')

    plt.legend(loc='upper left', shadow=False)
    cur_axes = plt.gca()
    cur_axes.axes.get_xaxis().set_visible(False)
    cur_axes.axes.get_yaxis().set_visible(False)
    #plt.savefig(out_file)
    plt.show()

""" Draws an interaction graph with nodes colored according to user category and
shaped according to cluster. """
def draw_color_and_shapenodes(G, out_file, interaction_type, node_lists, node_labels, k, clusters):
    plt.clf()
    print("getting layout")
    pos = nx.spring_layout(G)
    nx.draw_networkx_edges(G, pos, alpha=0.5, width=0.3, arrows=True)
    nodes = set(G.nodes())
    colors = ['r', 'g', 'b', 'k'] # for nodes
    shapes = ['s', '>', 'v', '<', 'd', 'p', 'h', '8'] # for clusters
    num_lists = len(node_lists)

    # add other nodes to end of node_lists
    other_nodes = nodes
    for i in range(num_lists):
        other_nodes = other_nodes - set(node_lists[i])
    node_lists.append(other_nodes)
    node_labels.append("others")
    num_lists += 1
    not_listed = nodes - set(list(clusters[:,0]))

    for i in range(num_lists):
        for j in range(k):
            curr_cluster = set(list(clusters[clusters[:,1] == str(j)][:,0]))
            curr_nodes = list(set(node_lists[i]).intersection(nodes).intersection(curr_cluster))
            nx.draw_networkx_nodes(G,pos, nodelist=curr_nodes, node_color=colors[i], node_shape=shapes[j],node_size=15,label=node_labels[i])
            print("drew list {}, cluster {}".format(i,j))
        curr_nodes = list(set(node_lists[i]).intersection(not_listed))
        nx.draw_networkx_nodes(G,pos, nodelist=curr_nodes, node_color=colors[i], node_shape='o',node_size=15,label=node_labels[i])
    plt.legend(loc='upper left', shadow=False)
    cur_axes = plt.gca()
    cur_axes.axes.get_xaxis().set_visible(False)
    cur_axes.axes.get_yaxis().set_visible(False)
    plt.savefig(out_file)

""" Draws an interaction graph with nodes colored according to user category and
shaped according to cluster and writes information about clusters in csv files."""
def draw_color_and_shapenodes_df(G, out_file, interaction_type, node_lists, node_labels, k, clusters):
    plt.clf()
    print("********************{}********************".format(out_file))
    pos = nx.spring_layout(G)
    nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.3, arrows=True)
    nodes = set(G.nodes())
    colors = ['r', 'g', 'b', 'k', 'c', 'm', 'y', '#551a8b', '#f4a460', '#ffc0cb', '#0d254c', '#18f5c6'] # for nodes
    shapes = ['.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', '+', 'x', 'D', 'l', '_'] # for clusters
    num_lists = len(node_lists)

    # add other nodes to end of node_lists
    other_nodes = nodes
    for i in range(num_lists):
        other_nodes = other_nodes - set(node_lists[i])
    node_lists.append(other_nodes)
    num_lists += 1
    not_listed = nodes - set(list(clusters.User))
    f = open("../Graphs/Clustering/Stats/Cluster_Info.csv", 'a')
    f2 = open("../Graphs/Clustering/Stats/Cluster_Stats.csv", 'a')
    for j in range(k):
        curr_cluster = set(list(clusters.loc[clusters.Partition == str(j), 'User']))
        for i in range(num_lists):
            curr_nodes = list(set(node_lists[i]).intersection(nodes).intersection(curr_cluster))
            nx.draw_networkx_nodes(G,pos, nodelist=curr_nodes, node_color=colors[i], node_shape=shapes[j],node_size=15,label=node_labels[i])
        curr_nodes = list(set(node_lists[i]).intersection(not_listed))
        nx.draw_networkx_nodes(G,pos, nodelist=curr_nodes, node_color='#ffa500', node_shape='_',node_size=15,label=node_labels[i])
    plt.legend(loc='upper left', shadow=False, prop={'size':6})
    cur_axes = plt.gca()
    cur_axes.axes.get_xaxis().set_visible(False)
    cur_axes.axes.get_yaxis().set_visible(False)
    plt.savefig(out_file)
    labeled_nodes = {}
    for node in other_nodes:
        labeled_nodes[node] = str(node)
    nx.draw_networkx_labels(G,pos, labels = labeled_nodes, font_size=6)
    plt.savefig(out_file + "_otherlabels")
    nx.draw_networkx_labels(G,pos, font_size=6)
    plt.savefig(out_file + "_alllabels")
    plt.clf()

    nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.3, arrows=True)
    max_percent_sum = 0
    min_percent_sum = 0

    last_slash_index = out_file.rfind("\\")
    cluster_method = out_file[last_slash_index + 1:]
    type_nums = [-1, -1, -1, -1]
    type_percents = [-1, -1, -1, -1]

    """ Draw graph with nodes colored according to cluster and shaped according
    to user category. """
    for i in range(k):
        curr_max = 0
        curr_min = 1

        curr_cluster = set(list(clusters.loc[clusters.Partition == str(i), 'User']))
        print("Cluster {} has {} members".format(i, len(curr_cluster)))
        cluster_subgraph = G.subgraph(curr_cluster)
        clustering_coef = nx.average_clustering(cluster_subgraph.to_undirected(), weight='weight')
        print("Cluster clustering coefficient: {}".format(clustering_coef))

        for j in range(num_lists):
            curr_nodes = list(set(node_lists[j]).intersection(nodes).intersection(curr_cluster))

            cluster_percent = len(curr_nodes) * 1.0 / len(curr_cluster)
            print("\t {} members are {} \t {}".format(len(curr_nodes), node_labels[j], cluster_percent))
            type_nums[j] = len(curr_nodes)
            type_percents[j] = cluster_percent
            if cluster_percent > curr_max:
                curr_max = cluster_percent
            if j < num_lists - 1 and cluster_percent < curr_min: # j < num_lists-1 so others aren't included
                curr_min = cluster_percent

            nx.draw_networkx_nodes(G,pos, nodelist=curr_nodes, node_color=colors[i],node_size=15)

        # Write stats to csv file
        try:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow([cluster_method, i, clustering_coef, type_percents[0], type_percents[1], type_percents[2], type_nums[0], type_nums[1], type_nums[2]])
        finally:
            pass
        max_percent_sum += curr_max * len(curr_cluster)
        min_percent_sum += curr_min * len(curr_cluster)

        curr_nodes = list(set(node_lists[j]).intersection(not_listed))
        nx.draw_networkx_nodes(G,pos, nodelist=curr_nodes, node_color=colors[i], node_size=15)
    cur_axes = plt.gca()
    cur_axes.axes.get_xaxis().set_visible(False)
    cur_axes.axes.get_yaxis().set_visible(False)
    plt.savefig(out_file + "_swapped")
    avg_max_percent = max_percent_sum / (len(nodes))
    avg_min_percent = min_percent_sum / (len(nodes))
    homog_score = cluster.homogeneity_score(clusters.Type, clusters.Partition)
    comp_score = cluster.completeness_score(clusters.Type, clusters.Partition)
    v_score = cluster.v_measure_score(clusters.Type, clusters.Partition)
    try:
        writer = csv.writer(f2, lineterminator='\n')
        writer.writerow([cluster_method, k, avg_max_percent, avg_min_percent, homog_score, comp_score, v_score])
    finally:
        f.close()
        f2.close()

""" Return a subset of a graph including only edges going to a specified set of
nodes. """
def create_graph_subset(G, node_list):
    return util.get_edges_to(G, node_list)

""" Add user categories as attributes in a given graph. """
def add_types(g):
    nodes = g.nodes()
    length = len(nodes)
    d = {}
    for i in range(length):
        user = nodes[i]
        if user in c_list:
            d[user] = 'c'
        elif user in p_list:
            d[user] = 'p'
        elif user in m_list:
            d[user] = 'm'
    nx.set_node_attributes(g, 'type', d)

""" Prints information about attribute mixing. """
def attribute_info():
    c_list, m_list, p_list = util.get_lists()
    cmp_list = util.append_arrays(c_list, m_list, p_list)

    interaction_types = ['mentions', 'replies', 'retweets']
    for interaction_type in interaction_types:
        edge_list = util.get_edge_list(interaction_type)
        g = create_graph_edge_weights(edge_list)
        cmp_g = create_graph_subset(g, cmp_list)
        add_types(cmp_g)
        print('{} Assortativity: '.format(interaction_type), nx.attribute_assortativity_coefficient(cmp_g,'type'))
        print('{} Mixing: '.format(interaction_type), nx.attribute_mixing_dict(cmp_g, 'type', normalized=True))
    
def main():
    attribute_info()

if __name__ == "__main__":
    main()
