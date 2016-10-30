import graph_creator as gc
import graph_utils as util
import pymysql.cursors
import sys


def lists_into_database(c_list, m_list, p_list):
    connection = pymysql.connect(host='localhost',
                                user='root',
                                password='password',
                                db='iw03',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    print("opened connection")
    i = 0
    try:
        with connection.cursor() as cursor:
            # add types into database
            # create tables with lists
            sql = "INSERT INTO `c_list` (`name`) VALUES (%s)"
            for i in range(len(c_list)):
                cursor.execute(sql, (c_list[i]))
            sql = "INSERT INTO `m_list` (`name`) VALUES (%s)"
            for i in range(len(m_list)):
                cursor.execute(sql, (m_list[i]))
            sql = "INSERT INTO `p_list` (`name`) VALUES (%s)"
            for i in range(len(p_list)):
                cursor.execute(sql, (p_list[i]))
        connection.commit()
    finally:
        connection.close()

def degrees_into_database(G, c_list, m_list, p_list, table_name):
    weight='weight'

    pG_in = util.get_edges_from(G, p_list)
    mG_in = util.get_edges_from(G, m_list)
    cG_in = util.get_edges_from(G, c_list)

    p_indeg = pG_in.in_degree(weight=weight)
    m_indeg = mG_in.in_degree(weight=weight)
    c_indeg = cG_in.in_degree(weight=weight)

    pG_out = util.get_edges_to(G, p_list)
    mG_out = util.get_edges_to(G, m_list)
    cG_out = util.get_edges_to(G, c_list)
    p_outdeg = pG_out.out_degree(weight=weight)
    m_outdeg = mG_out.out_degree(weight=weight)
    c_outdeg = cG_out.out_degree(weight=weight)
    t_outdeg = G.out_degree(weight=weight)

    # Write vectors of values
    nodes = G.nodes()
    num_nodes = len(nodes)
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='password',
                                 db='iw03',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    print("opened connection")
    i = 0
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO {} (`name`) VALUES (%s)".format(table_name)
            for i in range(num_nodes): # add node names into database
                cursor.execute(sql, (nodes[i]))
            sql = "UPDATE {} SET `type`=%s".format(table_name)
            cursor.execute(sql, ('o'))
            sql = "UPDATE {} SET `type`=%s WHERE name IN (SELECT name FROM c_list)".format(table_name)
            cursor.execute(sql, ('c'))
            sql = "UPDATE {} SET `type`=%s WHERE name IN (SELECT name FROM m_list)".format(table_name)
            cursor.execute(sql, ('m'))
            sql = "UPDATE {} SET `type`=%s WHERE name IN (SELECT name FROM p_list)".format(table_name)
            cursor.execute(sql, ('p'))

            sql = "UPDATE {} SET {}=%s WHERE `name`=%s"
            currSql = sql.format(table_name, '`p_indeg`')
            for key, value in p_indeg.items():
                cursor.execute(currSql, (value, key))
            currSql = sql.format(table_name, '`m_indeg`')
            for key, value in m_indeg.items():
                cursor.execute(currSql, (value, key))
            currSql = sql.format(table_name, '`c_indeg`')
            for key, value in c_indeg.items():
                cursor.execute(currSql, (value, key))
            currSql = sql.format(table_name, '`p_outdeg`')
            for key, value in p_outdeg.items():
                cursor.execute(currSql, (value, key))
            currSql = sql.format(table_name, '`m_outdeg`')
            for key, value in m_outdeg.items():
                cursor.execute(currSql, (value, key))
            currSql = sql.format(table_name, '`c_outdeg`')
            for key, value in c_outdeg.items():
                cursor.execute(currSql, (value, key))
            currSql = sql.format(table_name, '`t_outdeg`')
            for key, value in t_outdeg.items():
                cursor.execute(currSql, (value, key))
            sql = "UPDATE {} SET `o_outdeg`=`t_outdeg`-`p_outdeg`-`m_outdeg`-`c_outdeg`".format(table_name)
            cursor.execute(sql)
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
        print("committed changes")
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `id`, `name`, `p_indeg` FROM {} WHERE `type`=%s".format(table_name)
            cursor.execute(sql, ('p',))
            result = cursor.fetchone()
            print(result)
    finally:
        connection.close()

def main():
    c_list, m_list, p_list = util.create_lists()
    lists_into_database(c_list, m_list, p_list)
    retweet_edge_list = util.get_edge_list('retweets');
    print("created retweets edge list")
    retweet_g = gc.create_graph_edge_weights(retweet_edge_list)
    print("created retweets graph")
    degrees_into_database(retweet_g, c_list, m_list, p_list, '`retweetsvectors`')
    print("entered into retweets database")

    mentions_edge_list = util.get_edge_list('mentions');
    print("created mentions edge list")
    mentions_g = gc.create_graph_edge_weights(mentions_edge_list)
    print("created mentions graph")
    degrees_into_database(mentions_g, c_list, m_list, p_list, '`mentionsvectors`')
    print("entered into mentions database")

    replies_edge_list = util.get_edge_list('replies');
    print("created replies list")
    replies_g = gc.create_graph_edge_weights(replies_edge_list)
    print("created replies graph")
    degrees_into_database(replies_g, c_list, m_list, p_list, '`repliesvectors`')
    print("entered into replies database")

    hashtags_edge_list = util.get_edge_list('hashtags');
    print("created hashtags list")
    hashtags_g = gc.create_graph_edge_weights(hashtags_edge_list)
    print("created hashtags graph")
    degrees_into_database(hashtags_g, c_list, m_list, p_list, '`hashtagsvectors`')
    print("entered into hashtags database")
if __name__ == "__main__":
    main()
