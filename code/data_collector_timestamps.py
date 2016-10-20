"""
Includes timestamps in csv edge lists.
"""
import csv #Import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import time
import tweepy

# assuming twitter_authentication.py contains each of the 4 oauth elements (1 per line)
from twitter_authentication import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

def authorize():
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    return tweepy.API(auth)

def get_account_names(info_file):
    ACCOUNT_COL = 0
    info =  np.loadtxt(info_file, dtype=str, delimiter=',', skiprows=1)
    return info[:,ACCOUNT_COL]

def get_statuses(username):
    print 'Retrieving info for {}'.format(username)
    RATE_LIMIT_CODE = 88
    tweepy_api = authorize()
    statuses = []
    count = 200;
    first_set = True
    while(first_set == True or len(new_tweets) > 0):
        # print "Length of statuses", len(statuses)
        # print "New tweets", len(new_tweets)
        try:
            if first_set:
                new_tweets = tweepy_api.user_timeline(screen_name=username, count=count, include_rts=True)
                first_set = False
            else:
                max_id = (statuses[-1].id) - 1 # id of last retrieved tweet
                new_tweets = tweepy_api.user_timeline(username, count=count, include_rts=True, max_id = max_id)
            statuses += new_tweets
        except KeyError, e: # No more results when next_results doesn't exist
            break
        except tweepy.RateLimitError as e:
            print 'Error {}.'.format(e)
            print 'Currently at {} statuses for account {}'.format(len(statuses), username)
            print 'Rate limit error. Sleeping for 15 minutes. Current time: {}'.format(time.localtime())
            time.sleep(60 * 15)
        except Exception as e:
            print 'Exception {}'.format(e)
            print 'Currently at {} statuses for account {}'.format(len(statuses), username)
    return statuses

def write_info(status, statusesWriter, mentionsWriter, retweetsWriter, repliesWriter, hashtagsWriter):
    username = status.user.screen_name
    #Write a row to the csv file/ I use encode utf-8
    statusesWriter.writerow([username, status.created_at, status.text.encode('utf-8'), status.favorite_count, status.id, status.entities['hashtags'], status.entities['user_mentions'], status.in_reply_to_screen_name])
    # Write a row for each mention
    for user_mention in status.entities['user_mentions']:
        mentionsWriter.writerow([username, user_mention['screen_name'], status.created_at])

    # Write a row if it's a retweet
    if hasattr(status, 'retweeted_status'):
        retweetsWriter.writerow([username, status.retweeted_status.user.screen_name, status.created_at])

    # Write a row if it's a reply
    if status.in_reply_to_screen_name != None:
        repliesWriter.writerow([username, status.in_reply_to_screen_name, status.created_at])

    # Write a row for each hashtags
    for hashtag in status.entities['hashtags']:
        hashtagsWriter.writerow([username, hashtag['text'].encode('utf-8'), status.created_at])

def write_info_to_files(account_names, statusesWriter, mentionsWriter, retweetsWriter, repliesWriter, hashtagsWriter, counterWriter):
    total_statuses = 0;
    for username in account_names:
        statuses = get_statuses(username)
        print 'Retrieved {} statuses for {}'.format(len(statuses), username)
        counterWriter.writerow([username, len(statuses)])
        total_statuses += len(statuses)
        print "total statuses {}".format(total_statuses)
        for status in statuses:
            write_info(status, statusesWriter, mentionsWriter, retweetsWriter, repliesWriter, hashtagsWriter)

def write_all_info(statusesFileName, mentionsFileName, retweetsFileName, repliesFileName, hashtagsFileName, accountsFileName):
    statusesFile = open(statusesFileName, 'a')
    mentionsFile = open(mentionsFileName, 'a')
    retweetsFile = open(retweetsFileName, 'a')
    repliesFile = open(repliesFileName, 'a')
    hashtagsFile = open(hashtagsFileName, 'a')

    account_names = get_account_names(accountsFileName)

    statusesWriter = csv.writer(statusesFile, lineterminator='\n')
    mentionsWriter = csv.writer(mentionsFile, lineterminator='\n')
    retweetsWriter = csv.writer(retweetsFile, lineterminator='\n')
    repliesWriter =  csv.writer(repliesFile, lineterminator='\n')
    hashtagsWriter = csv.writer(hashtagsFile, lineterminator='\n')

    write_info_to_files(account_names, statusesWriter, mentionsWriter, retweetsWriter, repliesWriter, hashtagsWriter)

    statusesFile.close()
    mentionsFile.close()
    retweetsFile.close()
    repliesFile.close()
    hashtagsFile.close()

# Main
def main():
    # Politicians
    statusesFileName = "politicians_statuses_timestamps.csv"
    mentionsFileName = "politicians_mentions_timestamps.csv"
    retweetsFileName = "politicians_retweets_timestamps.csv"
    hashtagsFileName = "politicians_hashtags_timestamps.csv"
    accountsFileName = "politicianslist.csv"
    write_all_info(statusesFileName, mentionsFileName, retweetsFileName, repliesFileName, hashtagsFileName, accountsFileName)

    # Senators
    statusesFileName = "senators_statuses_timestamps.csv"
    mentionsFileName = "senators_mentions_timestamps.csv"
    retweetsFileName = "senators_retweets_timestamps.csv"
    hashtagsFileName = "senators_hashtags_timestamps.csv"
    accountsFileName = "senatorslist.csv"
    write_all_info(statusesFileName, mentionsFileName, retweetsFileName, repliesFileName, hashtagsFileName, accountsFileName)

    # Media
    statusesFileName = "media_statuses_timestamps.csv"
    mentionsFileName = "media_mentions_timestamps.csv"
    retweetsFileName = "media_retweets_timestamps.csv"
    hashtagsFileName = "media_hashtags_timestamps.csv"
    accountsFileName = "medialist.csv"
    write_all_info(statusesFileName, mentionsFileName, retweetsFileName, repliesFileName, hashtagsFileName, accountsFileName)

    # Celebrities
    statusesFileName = "celebrities_statuses_timestamps.csv"
    mentionsFileName = "celebrities_mentions_timestamps.csv"
    retweetsFileName = "celebrities_retweets_timestamps.csv"
    hashtagsFileName = "celebrities_hashtags_timestamps.csv"
    accountsFileName = "celebritieslist.csv"
    write_all_info(statusesFileName, mentionsFileName, retweetsFileName, repliesFileName, hashtagsFileName, accountsFileName)

if __name__ == "__main__":
    main()
