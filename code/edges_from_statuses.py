import numpy as np
import pandas as pd
import string as st
import sys

def statuses_from_file(statuses_file):
    df = pd.read_csv(statuses_file, sep=',', header=None)
    df.fillna("None")
    return df.values

""" Returns a numpy array of hashtags (each row of the form [username, hashtag])
from a numpy array of statuses collected using data_collector.py. """
def hashtags_from_statuses(statuses):
    initialized = False
    for i in range(statuses.shape[0]):
        username = statuses[i, username_col]
        status_hashtags = hashtags_from_status(username, statuses[i,hashtag_col])
        if status_hashtags != None:
            if initialized == False:
                initialized = True
                hashtags = status_hashtags
            else:
                hashtags = np.concatenate((hashtags, status_hashtags), axis=0)
    return hashtags

#TODO: retweetsFile
#TODO: replies

""" Returns a numpy array of hashtags (each row of the form [username, hashtag])
from a hashtag entity list represented as a string. """
def hashtags_from_status(username, ht):
    start = 5
    skip = 0
    hashtags = words_from_string(ht, start, skip)
    if hashtags == None:
        return hashtags
    num_hashtags = hashtags.size
    username_array = np.reshape(np.repeat(np.array([username]), num_hashtags, axis=0), (num_hashtags, 1))
    return np.concatenate((username_array, hashtags), axis=1)

""" Returns the desired username(s), given information about apostrophe usage. """
def words_from_string(string, start, skip):
    values = None
    index = 0
    signal = "'"
    n = 5
    while True:
        index = skip_n_signals(string, signal, index, n)
        if index == -1:
            return values
        end_index = st.find(string, signal, index + 1)
        value = np.reshape(np.array([string[index + 1:end_index]]), (1, 1))
        if values == None:
            values = value
        else:
            values = np.concatenate((values, value), axis=0)
        index = end_index
        index = skip_n_signals(string, signal, index, skip)
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
    global username_col, time_col, hashtag_col, retweets_col, replies_col
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
    hashtags_from_statuses(statuses)
if __name__ == "__main__":
    main()
