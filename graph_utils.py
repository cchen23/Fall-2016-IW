"""
graph_utils.py

Descrition: Utility methods
"""
import networkx as nx
import numpy as np
import numpy.lib.recfunctions as rec
import pandas as pd
import pymysql.cursors

""" Returns an array created by appending all the rows in a given set of arrays. """
def append_arrays(*args):
    full_array = args[0]
    for i in range(1, len(args)):
        full_array = np.concatenate((full_array, args[i]), axis=0)
    return full_array

""" Returns a numpy array of values contained in the columns start_col:end_col
in a given file, converted to lowercase. """
def array_from_file(start_col, end_col, array_file, skiprows):
    info = np.char.lower(np.loadtxt(array_file, usecols = range(start_col,end_col), dtype=str, delimiter=',', skiprows=skiprows))
    return info

""" Given a list of users in each category, labels each user in a given list. """
def add_types(users, c_list, m_list, p_list):
    length = vector.shape[0]
    for i in range(length):
        user = users[i]['name']
        if user in c_list:
            users[i]['type'] = 'c'
        elif user in p_list:
            users[i]['type'] = 'p'
        elif user in m_list:
            users[i]['type'] = 'm'
        else:
            users[i]['type'] = 'o'
    return

""" Returns a list of edges corresponding to a given interaction type from the
database."""
def get_edge_list(interaction_type):
    connection = pymysql.connect(host='localhost',
                                user='root',
                                password='password',
                                db='iw03',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `start_node`, `end_node` FROM {}_edges"
            cursor.execute(sql.format(interaction_type))
            results = cursor.fetchall()
            edge_list = pd.DataFrame(results)
            edge_list['start_node'] = map(lambda x: str(x).lower(), edge_list['start_node'])
            edge_list.end_node = edge_list.end_node.str.encode("ascii", "ignore")
            edge_list['end_node'] = map(lambda x: str(x).lower(), edge_list['end_node'])
            connection.commit()
    finally:
        connection.close()
    return edge_list

""" Returns graph with edges starting from a certain list of nodes."""
def get_edges_from(G, list):
    G=nx.DiGraph( [ (u,v,d) for u,v,d in G.edges(data=True) if u in list])
    return G

""" Returns graph with edges going to a certain list of nodes."""
def get_edges_to(G, nodes_list):
    G=nx.DiGraph( [ (u,v,d) for u,v,d in G.edges(data=True) if v in nodes_list])
    return G

""" Returns dataframes with info about celebrities, media outlets, and
politicians. NOTE: Contains hadcoded filenames. """
def get_list_dfs():
    c_file = "C:\Users\Cathy\Documents\Courses\\2016-2017\IW03\Data\celebritieslistlabeled.csv"
    m_file = "C:\Users\Cathy\Documents\Courses\\2016-2017\IW03\Data\medialistlabeled.csv"
    p_file = "C:\Users\Cathy\Documents\Courses\\2016-2017\IW03\Data\politicianslistlabeled.csv"
    dtypes = {'User': str, 'Name': str, 'Following': str, 'Followers': str, 'Affiliation': str, 'Description': str}
    c_df = pd.read_csv(c_file, header=0, names=['User', 'Name', 'Following', 'Followers', 'Description'], index_col=False, dtype=dtypes)
    c_df.User = c_df.User.str.lower()
    m_df = pd.read_csv(m_file, header=0, names=['User', 'Name', 'Following', 'Followers', 'Description'], index_col=False, dtype=dtypes)
    m_df.User = m_df.User.str.lower()
    p_df = pd.read_csv(p_file, header=0, names=['User', 'Name', 'Following', 'Followers', 'Affiliation', 'Description'], index_col=False, dtype=dtypes)
    p_df.User = p_df.User.str.lower()
    return c_df, m_df, p_df

""" Returns lists of celebrities, media outlets, and politicians. """
def get_lists():
    connection = pymysql.connect(host='localhost',
                                user='root',
                                password='password',
                                db='iw03',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `name` FROM {}"

            cursor.execute(sql.format('`c_list`'))
            results = cursor.fetchall()
            c_list = pd.DataFrame(results)
            c_list['name'] = map(lambda x: str(x).lower(), c_list['name'])

            cursor.execute(sql.format('`m_list`'))
            results = cursor.fetchall()
            m_list = pd.DataFrame(results)
            m_list['name'] = map(lambda x: str(x).lower(), m_list['name'])

            cursor.execute(sql.format('`p_list`'))
            results = cursor.fetchall()
            p_list = pd.DataFrame(results)
            p_list['name'] = map(lambda x: str(x).lower(), p_list['name'])

        connection.commit()
    finally:
        connection.close()
    return c_list['name'].values.tolist(), m_list['name'].values.tolist(), p_list['name'].values.tolist()
