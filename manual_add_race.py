#!/usr/bin/python
# coding: utf8

import ConfigParser
import bs4, requests
import os
import email_notification
import datetime
import message_groupme
import sqlite3
import xmltodict
import sys


def get_db_conn():
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')
    db_path = config.get('database', 'auto_close')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return conn, c


def add_race_watch(raceID, max_pilots):
    # This will add a race to the watch list.
    body = "Adding Race {} to watch list.".format(raceID)
    # print(body)
    conn, c = get_db_conn()
    c.execute('''SELECT * FROM races WHERE raceID=?''', (raceID,))
    i_check = c.fetchone()
    if i_check:
        body = 'Already watching RaceID {} with a Max Pilots of {}.\n' \
               'I am going to check to see if it needs updated.'.format(i_check[0], i_check[1])
        # print(body)
        update_race_watch(raceID, max_pilots)
    else:
        c.execute('''INSERT INTO races (raceID, max_pilots, notified, c_count) VALUES(?,?,?,?)''',
                  (raceID, max_pilots, False, 0))
        conn.commit()
        c.execute('''SELECT * FROM races WHERE raceID=?''', (raceID,))
        validate = c.fetchone()
        if validate:
            initial_data_grab(raceID, c, conn)
            c.execute('''SELECT * FROM races WHERE raceID=?''', (raceID,))
            current = c.fetchone()
            body = "Added RaceID {} with a Max Pilots of {}.\n" \
                   "Race currently has {} pilots signed up.".format(current[0], current[1], current[3])
            print(body)

    conn.close()


def initial_data_grab(raceID, c, conn):
    res = requests.get('http://www.multigp.com/races/view/{}/'.format(raceID))
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    count = len(soup.select('.list-view .row'))

    c.execute('''UPDATE races SET "c_count"=? WHERE raceID=?''', (count, raceID))
    conn.commit()


def update_race_watch(raceID, max_pilots):
    # This will update a race already being watched.
    body = "Updating Race {} to Max Pilots {}.".format(raceID, max_pilots)
    print(body)

    conn, c = get_db_conn()
    c.execute('''SELECT * FROM races WHERE raceID=?''', (raceID,))
    pre_check = c.fetchone()
    if pre_check:
        if pre_check[1] != int(max_pilots):
            c.execute('''UPDATE races SET max_pilots=? WHERE raceID=?''', (max_pilots, raceID))
            conn.commit()
            c.execute('''SELECT * FROM races WHERE raceID=?''', (raceID,))
            validate = c.fetchone()
            if validate:
                body = "Updated Race {} to Max Pilots of {}.".format(validate[0], validate[1])
                print(body)
        else:
            body = "No changes made. Already watching for Max Pilots of {} for Race {}".format(max_pilots, raceID)
            print(body)
    else:
        body = 'Race {} doesn\'t exist...\n' \
               'Going to add it for you.'.format(raceID)
        print(body)
        add_race_watch(raceID, max_pilots)

    conn.close()


if __name__ == '__main__':
    raceID = sys.argv[1]
    pilots = sys.argv[2]
    add_race_watch(raceID, pilots)