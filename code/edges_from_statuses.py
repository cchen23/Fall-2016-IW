"""
Extracts edges information from a csv file of statuses collected using
data_collector.py
"""
import numpy as np
import pandas as pd
import string as st
import sys

def statuses_from_file(statuses_file):
    df = pd.read_csv(statuses_file, sep=',', header=None)
    df = df.fillna("None")
    return df.values

def hashtags_from_statuses(statuses):
    before = 5
    after = 0
    return edges_from_statuses(statuses, hashtag_col, before, after)

def mentions_from_statuses(statuses):
    before = 11
    after = 4
    return edges_from_statuses(statuses, mentions_col, before, after)

def replies_from_statuses(statuses):
    replies_data = statuses[:,[username_col, replies_col]]
    mask = replies_data[:,1] != "None"
    return replies_data[mask]

def retweets_from_statuses(statuses):
    initialized = False
    signal_rt = "RT @"
    signal_end = ":"
    for i in range(statuses.shape[0]):
        username = statuses[i, username_col]
        content = statuses[i, content_col]
        if st.find(content, signal_rt) > -1:
            start = st.find(content, signal_rt)
            end = st.find(content, signal_end)
            retweet_name = content[start + 4:end]
            retweet = np.reshape(np.array([username, retweet_name]), (1, 2))
            if not initialized:
                initialized = True
                retweets = retweet
            else:
                retweets = np.concatenate((retweets, retweet), axis=0)
    return retweets

""" Returns a numpy array of hashtags (each row of the form [username, hashtag])
from a numpy array of statuses collected using data_collector.py. """
def edges_from_statuses(statuses, col, before, after):
    initialized = False
    for i in range(statuses.shape[0]):
        username = statuses[i, username_col]
        status_edges = edges_from_status(username, statuses[i,col], before, after)
        if status_edges is not None:
            if initialized == False:
                initialized = True
                edges = status_edges
            else:
                edges = np.concatenate((edges, status_edges), axis=0)
    return edges

""" Returns a numpy array of hashtags (each row of the form [username, hashtag])
from a hashtag entity list represented as a string. """
def edges_from_status(username, string, before, after):
    edges = info_from_string(string, before, after)
    if edges is None:
        return edges
    num_edges = edges.size
    username_array = np.reshape(np.repeat(np.array([username]), num_edges, axis=0), (num_edges, 1))
    return np.concatenate((username_array, edges), axis=1)

""" Retrieves words from a string based on apostrophe positions. Retrieves the
word following the num_before'th apostrophe, and starts a new cycle after skipping
num_after more apostrophes."""
def info_from_string(string, num_before, num_after):
    values = None
    index = 0
    signal = "'"
    while True:
        index = skip_n_signals(string, signal, index, num_before)
        if index == -1:
            return values
        end_index = st.find(string, signal, index + 1)
        value = np.reshape(np.array([string[index + 1:end_index]]), (1, 1))
        if values is None:
            values = value
        else:
            values = np.concatenate((values, value), axis=0)
        index = end_index
        index = skip_n_signals(string, signal, index, num_after)
        if index == -1:
            return values

def skip_n_signals(string, signal, index, n):
    for i in range(n):
        last_index = index + 1
        index = st.find(string, signal, last_index)
        if index == -1:
            return index
    return index

""" The columnnames of statuses stored using data_collector.py. """
def set_colnames():
    global username_col, time_col, content_col, hashtag_col, retweets_col, replies_col
    username_col = 0
    time_col = 1
    content_col = 2
    hashtag_col = 5
    mentions_col = 6
    replies_col = 7

def main():
    statuses_file = sys.argv[1]
    set_colnames()
    statuses = statuses_from_file(statuses_file)
    print statuses.shape
    print hashtags_from_statuses(statuses)
    retweets = retweets_from_statuses(statuses)
    print retweets
    print replies_from_statuses(statuses)
if __name__ == "__main__":
    main()
