"""
data_collector.py

Description: Retrieves Twitter interactions for specified users and saves them
in a SQL database.
"""
import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import pymysql.cursors
import sys
import time
import tweepy

# assuming twitter_authentication.py contains each of the 4 oauth elements (1 per line)
from twitter_authentication import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

""" Authorize program to use Twitter API. """
def authorize():
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    return tweepy.API(auth)

""" Get Twitter account names from a csv file that contains account names in the
first column. """
def get_account_names(info_file):
    ACCOUNT_COL = 0
    info =  np.loadtxt(info_file, dtype=str, delimiter=',', skiprows=1)
    return info[:,ACCOUNT_COL]

""" Retrieves maximum number of statuses for a certain username. """
def get_statuses(username):
    print 'Retrieving info for {}'.format(username)
    RATE_LIMIT_CODE = 88
    tweepy_api = authorize()
    statuses = []
    count = 200;
    first_set = True
    while(first_set == True or len(new_tweets) > 0):
        try:
            if first_set: # Retrieve the first 'count' Tweets
                new_tweets = tweepy_api.user_timeline(screen_name=username, count=count, include_rts=True)
                first_set = False
            else: # Retrieve 'count' Tweets, starting from the last collected Tweet
                max_id = (statuses[-1].id) - 1 # id of last retrieved tweet
                new_tweets = tweepy_api.user_timeline(username, count=count, include_rts=True, max_id = max_id)
            statuses += new_tweets
        except KeyError, e: # No more results for this user
            break
        except tweepy.RateLimitError as e: # Hit rate limit, so sleep for 15 minutes
            print 'Error {}.'.format(e)
            print 'Currently at {} statuses for account {}'.format(len(statuses), username)
            print 'Rate limit error. Sleeping for 15 minutes. Current time: {}'.format(time.localtime())
            time.sleep(60 * 15)
        except Exception as e: # If other exceptions (ex. internet connection interrupted), try again
            print 'Exception {}'.format(e)
            print 'Currently at {} statuses for account {}'.format(len(statuses), username)
    return statuses

""" Write a status to the database. """
def write_status(name, time_created, text, favorite_count):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `statuses` (`name`, `time_created`, `text`, `favorite_count`) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (name, time_created, text, favorite_count))
    connection.commit()

""" Write an edge to the database. """
def write_edge(sql, start, end, time):
    with connection.cursor() as cursor:
        cursor.execute(sql, (start, end, time))
    connection.commit()

""" Write interaction edges in a given status into the respective database. """
def write_info(status):
    username = status.user.screen_name

    write_status(username, status.created_at, status.text.encode('utf-8'), status.favorite_count)

    sql = "INSERT INTO {} (`start_node`, `end_node`, `time_created`) VALUES (%s, %s, %s)"

    # Write a row for each mention
    mentions_sql = sql.format('`mentions_edges`')
    for user_mention in status.entities['user_mentions']:
        write_edge(mentions_sql, username, user_mention['screen_name'], status.created_at)

    # Write a row if it's a retweet
    if hasattr(status, 'retweeted_status'):
        write_edge(sql.format('`retweets_edges`'), username, status.retweeted_status.user.screen_name, status.created_at)

    # Write a row if it's a reply
    if status.in_reply_to_screen_name != None:
        write_edge(sql.format('`replies_edges`'), username, status.in_reply_to_screen_name, status.created_at)

    # Write a row for each hashtag
    hashtags_sql = sql.format('`hashtags_edges`')
    for hashtag in status.entities['hashtags']:
        write_edge(hashtags_sql, username, hashtag['text'].encode('utf-8'), status.created_at)

""" Write interaction edges for all statuses from a given list of account names into the database. """
def write_info_to_database(account_names):
    total_statuses = 0;
    for username in account_names:
        statuses = get_statuses(username)
        earliest = statuses[-1].created_at
        latest = statuses[0].created_at
        print 'Retrieved {} statuses for {}'.format(len(statuses), username)
        print 'Earliest retrieved status was {} and latest status was {}'.format(earliest, latest)
        total_statuses += len(statuses)
        print "total statuses {}".format(total_statuses)
        for status in statuses:
            write_info(status)

""" Get a list of account names and write statuses and interaction edges for all
of the accounts into the database. """
def write_all_info(accountsFileName):
    account_names = get_account_names(accountsFileName)
    write_info_to_database(account_names)

def main():
    global connection
    connection = pymysql.connect(host='localhost',
                                user='root',
                                password='password',
                                db='iw03',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    print("opened connection")
    # Politicians
    accountsFileName = "C:\Users\Cathy\Documents\Courses\\2016-2017\IW03\Data\politicianslist.csv"
    write_all_info(accountsFileName)

    # Media
    accountsFileName = "C:\Users\Cathy\Documents\Courses\\2016-2017\IW03\Data\medialist.csv"
    write_all_info(accountsFileName)

    # Celebrities
    accountsFileName = "C:\Users\Cathy\Documents\Courses\\2016-2017\IW03\Data\celebritieslist.csv"
    write_all_info(accountsFileName)
    connection.close()

if __name__ == "__main__":
    main()
