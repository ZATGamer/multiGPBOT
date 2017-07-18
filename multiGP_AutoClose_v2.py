#!/usr/bin/python

import ConfigParser
import bs4, requests
import os
import email_notification
import datetime
import message_groupme
import sqlite3


def close_race(count):
    close_url = ''
    # close_url = 'http://www.multigp.com/multigp/race/close/id/9369'
    # print(close_url)
    # close_race_code = session.post(close_url)
    # close_race_code = session.get(close_url)

    # update_race_data = session.get('http://www.multigp.com/multigp/race/updateRaceEntries/id/9369')

    # print("Race CLOSED status code: {}".format(close_race_code.status_code))
    print("Race has Reached Limit ({} Pilots). CLOSE IT!".format(count))
    if not notified:
        print("Sending Notice")
        body = 'Time to close the race! Has {} out of {} Pilots.\n ' \
               'Close URL: "http://www.multigp.com/multigp/race/close/id/{}"'.format(count, max_pilots, raceID)
        subject = "CLOSE THE RACE!"
        send_notice(subject, body)
        c.execute('''UPDATE races SET notified=? WHERE raceID=?''', (True, raceID))
        conn.commit()

    else:
        print("Already notified.")


def check_race(raceID, max_pilots, old_count):
    res = requests.get('http://www.multigp.com/races/view/{}/'.format(raceID))
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    count = len(soup.select('.list-view .row'))

    print('Race currently has {} pilots. Out of {}. -- {}'.format(count, max_pilots, datetime.datetime.now()))

    if count != old_count:
        c.execute('''UPDATE races SET "count"=? WHERE raceID=?''', (count, raceID))
        conn.commit()

    print("Count: {} Max:{}".format(count, max_pilots))
    if count >= max_pilots:
        close_race(count)


def delete_notified(raceID):
    c.execute('''DELETE FROM races WHERE raceID=?''', (raceID,))
    conn.commit()
    subject = "Stoped Watching Race"
    body = "I have stopped watching raceID {}".format(raceID)
    send_notice(subject, body)


def send_notice(subject, body):
    # email_notification.send_notification(subject, body)
    message_groupme.send_message(body)


def create_db():
    print('Running first time db setup.')
    db_path = config.get('database', 'auto_close')
    with open(db_path, 'ab'):
        pass
    # Connect to the database
    db_conn = sqlite3.connect(db_path)
    db_c = db_conn.cursor()
    # Create table
    db_c.execute('''CREATE TABLE races (raceID INTEGER PRIMARY KEY, max_pilots INTEGER, notified, count INTEGER)''')
    db_conn.commit()


def start_up():
    # stuff to run at start up. Does basic check like if the DB has been created or not. If not then create it.
    if not os.path.exists(config.get('database', 'auto_close')):
        create_db()


if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')

    start_up()

    db_path = config.get('database', 'auto_close')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''SELECT * FROM races''')
    races = c.fetchall()

    for race in races:
        raceID = race[0]
        max_pilots = race[1]
        notified = race[2]
        old_count = race[3]

        if not notified:
            check_race(raceID, max_pilots, old_count)
        else:
            print("Already Notified deleting")
            delete_notified(raceID)
            c.execute('''SELECT * FROM races''')
            test = c.fetchall()
            for crap in test:
                print test

    conn.close()
