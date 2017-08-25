#!/usr/bin/python

import ConfigParser
import bs4, requests
import os
import email_notification
import datetime
import message_groupme
import sqlite3
import xmltodict


def send_close_notice(count):
    # close_url = ''
    # close_url = 'http://www.multigp.com/mgp/multigp/race/close/id/10051'
    # print(close_url)
    # close_race_code = session.post(close_url)
    # close_race_code = session.get(close_url)

    # update_race_data = session.get('http://www.multigp.com/multigp/race/updateRaceEntries/id/9369')

    # print("Race CLOSED status code: {}".format(close_race_code.status_code))
    print("Race has Reached Limit ({} Pilots). CLOSE IT!".format(count))
    if not notified:
        print("Sending Notice")
        body = 'Time to close the race!\n' \
               '{}\n' \
               'Has {} out of {} Pilots.\n ' \
               'Close URL: "http://www.multigp.com/mgp/multigp/race/close/id/{}"'.format(title, count, max_pilots, raceID)
        subject = "CLOSE THE RACE!"
        send_notice(subject, body)
        c.execute('''UPDATE races SET notified=? WHERE raceID=?''', (True, raceID))
        conn.commit()

    else:
        print("Already notified.")


def check_race(raceID, max_pilots, old_count):
    res = requests.get('http://www.multigp.com/mgp/races/view/{}/'.format(raceID))
    # res = requests.get('http://www.multigp.com/mgp/races/view/{}/')
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    count = len(soup.select('.list-view .row'))

    print('Race {} currently has {} pilots. Out of {}. -- {}'.format(raceID,
                                                                     count,
                                                                     max_pilots,
                                                                     datetime.datetime.now()))

    if count != old_count:
        c.execute('''UPDATE races SET "c_count"=? WHERE raceID=?''', (count, raceID))
        conn.commit()

    return count


def stop_watching(raceID):
    c.execute('''DELETE FROM races WHERE raceID=?''', (raceID,))
    conn.commit()
    subject = "Stopped Watching Race"
    body = "Race {} has been closed.".format(raceID)
    send_notice(subject, body)


def get_name(raceID):
    print('Getting the name of the race {}.'.format(raceID))
    
    res = requests.get('http://www.multigp.com/mgp/races/view/{}/'.format(raceID))
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    race_name = soup.select_one('h1').getText()
    race_name = race_name.strip()
    race_name = race_name.split('\n')
    race_name = race_name[0]

    c.execute('''UPDATE races SET title=? WHERE raceID=?''', (race_name, raceID))
    conn.commit()

    # try:
    #     print('Getting the name of the race {}.'.format(raceID))
    #     # Try and get the name from rss if it is not in the DB.
    #     rss_url = '{}{}'.format(config.get('multiGP', 'url'), config.get('chapter', 'rss_uri'))
    #     raw_race_data = requests.get(rss_url).content
    #
    #     # Convert the XML to something I can use
    #     races_response = xmltodict.parse(raw_race_data, process_namespaces=True)
    #
    #     # Create a Dict of all the data using the RaceID as the Key
    #     race_data = {}
    #     for race in races_response['rss']['channel']['item']:
    #         race_data[race['link'].split('/')[5]] = {'title': race['title'],
    #                                                  'link': race['link'],
    #                                                  'pubDate': race['pubDate'],
    #                                                  'description': race['description'],
    #                                                  'raceDate': race['title'].split('-')[-1]}
    #
    #     race_title = race_data[str(raceID)]['title']
    #     c.execute('''UPDATE races SET title=? WHERE raceID=?''', (race_title, raceID))
    #     conn.commit()
    # except:
    #     print("Race not in RSS Yet. Will try again next run.")


def is_closed(raceID):
    res = requests.get('http://www.multigp.com/mgp/races/view/{}/'.format(raceID))
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    status = soup.select_one('.fixed').getText()
    status = status.strip().lower()

    if status == 'closed':
        return True
    else:
        return False


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
    db_c.execute('''CREATE TABLE races (raceID INTEGER PRIMARY KEY,
                                        max_pilots INTEGER,
                                        notified,
                                        c_count INTEGER,
                                        title)''')
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

    if races:
        for race in races:
            raceID = race[0]
            max_pilots = race[1]
            notified = race[2]
            old_count = race[3]
            title = race[4]

            if not title:
                get_name(raceID)

            count = check_race(raceID, max_pilots, old_count)

            if count >= max_pilots:
                send_close_notice(count)

            if is_closed(raceID):
                stop_watching(raceID)

    else:
        print("No Races to check.")

    conn.close()
