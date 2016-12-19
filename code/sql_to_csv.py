"""
sql_to_csv.py

Description: Reads SQL tables into CSV files
"""
import csv
import MySQLdb
from UnicodeSupportForCsv import UnicodeWriter
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def sql_to_csv(table_name):
    conn = MySQLdb.Connection(db='iw03', host='localhost', user='root', passwd='password', use_unicode=0,charset='utf8')

    crsr = conn.cursor()
    crsr.execute("SELECT * FROM {};".format(table_name))

    with open(r'./DatabaseCSV/{}.csv'.format(table_name), 'wb') as csvfile:
        uw = UnicodeWriter(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        uw.writerow([i[0] for i in crsr.description]) # write headers

        for row in crsr.fetchall():
            uw.writerow([unicode(col) for col in row])

def main():
    table_names = ['hashtags_edges', 'mentions_edges', 'replies_edges', 'retweets_edges', 'statuses']
    for table_name in table_names:
        sql_to_csv(table_name)

if __name__ == "__main__":
    main()
