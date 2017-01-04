"""
json_writer.py

Description: Writes json files with nodes and edges of interaction graphs.
"""

import graph_creator as gc
import graph_utils as util
import networkx as nx

""" Add user categories as attributes in a given graph. """
def add_colors(g):
    c_list, m_list, p_list = util.get_lists()
    nodes = g.nodes()
    length = len(nodes)
    d = {}
    for i in range(length):
        user = nodes[i]
        if user in c_list:
            d[user] = 'red'
        elif user in p_list:
            d[user] = 'green'
        elif user in m_list:
            d[user] = 'blue'
    nx.set_node_attributes(g, 'color', d)

def write_graph_to_json(json_file, g, id_name):
    json_file.write("<script type=\"application/json\" id=\"{}\">".format(id_name))
    json_file.write("\n\t{\n\t\t \"nodes\":[")
    # write nodes
    nodes_list = g.nodes()
    num_nodes = len(nodes_list)
    print "num nodes: %s" % num_nodes
    colors=nx.get_node_attributes(g,'color')
    for i in range(num_nodes - 1):
        name = nodes_list[i]
        color = colors[name]
        json_file.write("{\n\t\t\t\"name\":\"%s\",\"color\":\"%s\"\n\t\t}" % (name, color))
        json_file.write(",")
    # write last node (no comma afterwards)
    json_file.write("{\n\t\t\t\"name\":\"%s\"\n\t\t}" % nodes_list[num_nodes - 1])

    json_file.write("],\n\t\t\"links\":[")

    # write edges
    edges_list = g.edges()
    num_edges = len(edges_list)
    print "num edges: %s" % num_edges
    for i in range(num_edges - 1):
        edge_tuple = edges_list[i]
        source = edge_tuple[0]
        source_num = nodes_list.index(source)
        target = edge_tuple[1]
        target_num = nodes_list.index(target)
        value = g.get_edge_data(source, target)['weight']
        json_file.write("{\n\t\t\t\"source\":%s,\"target\":%s,\"value\":%s\n\t\t}" % (source_num, target_num, value))
        json_file.write(",")

    # write last edge (no comma afterwards)
    edge_tuple = edges_list[num_edges - 1]
    source = edge_tuple[0]
    source_num = nodes_list.index(source)
    target = edge_tuple[1]
    target_num = nodes_list.index(target)
    value = g.get_edge_data(source, target)['weight']
    json_file.write("{\n\t\t\t\"source\":%s,\"target\":%s,\"value\":%s\n\t\t}]" % (source_num, target_num, value))

    json_file.write("\n\t}")
    json_file.write("\n</script>")
    return

def main():
    interaction_types = ['mentions', 'replies', 'retweets']

    for interaction_type in interaction_types:
            edge_list = util.get_edge_list(interaction_type)
            c_list, m_list, p_list = util.get_lists()
            c_df, m_df, p_df = util.get_list_dfs()
            node_lists = [c_list, m_list, p_list]
            node_labels = ["celebrities", "media", "politicians", "others"]
            cmp_list = util.append_arrays(c_list, m_list, p_list)
            g = gc.create_graph_edge_weights(edge_list)
            cmp_g = gc.create_graph_subset(g, cmp_list)
            add_colors(cmp_g)
            filename = "{}.json".format(interaction_type)
            json_file = open(filename, 'w')
            print "filename: %s" % filename
            write_graph_to_json(json_file, cmp_g, interaction_type[:3])
            json_file.close()

if __name__ == "__main__":
    main()
