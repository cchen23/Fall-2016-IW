"""
centralities.py

Description: Writes csv files with betweenness centrality, closeness centrality,
and PageRank for each node in interaction graphs.
"""
import csv
import networkx as nx
import graph_creator as gc
import graph_utils as util

def main():
    interaction_types = ['mentions', 'replies', 'retweets']

    for interaction_type in interaction_types:
        edge_list = util.get_edge_list(interaction_type)
        c_list, m_list, p_list = util.get_lists()
        c_df, m_df, p_df = util.get_list_dfs()
        node_lists = [c_list, m_list, p_list]
        cmp_list = util.append_arrays(c_list, m_list, p_list)
        G = gc.create_graph_edge_weights(edge_list)
        G = gc.create_graph_subset(G, cmp_list)

        # Page Rank
        pr = nx.pagerank(G)
        with open('{}_pagerank.csv'.format(interaction_type), 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in pr.items():
                writer.writerow([key, value])

        # Betweenness centrality
        bc = nx.betweenness_centrality(G)
        with open('{}_betweenness.csv'.format(interaction_type), 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in bc.items():
                writer.writerow([key, value])

        # Closeness centrality
        cc = nx.closeness_centrality(G)
        with open('{}_closeness.csv'.format(interaction_type), 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in cc.items():
                writer.writerow([key, value])

if __name__ == "__main__":
    main()
