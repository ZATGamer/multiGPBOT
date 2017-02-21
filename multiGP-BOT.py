#!/usr/bin/python

import os
import requests
import xmltodict
import sqlite3
import ConfigParser


def watch_rss():
    # Do a GET on the site for the RSS
    raw_race_data = session.get(rss_url).content

    # Convert the XML to something I can use
    races_responce = xmltodict.parse(raw_race_data, process_namespaces=True)

    # Create a Dict of all the data using the RaceID as the Key
    race_data = {}
    for race in races_responce['rss']['channel']['item']:
        race_data[race['link'].split('/')[5]] = {'title': race['title'],
                                                 'link': race['link'],
                                                 'pubDate': race['pubDate'],
                                                 'description': race['description'],
                                                 'raceDate': race['title'].split('-')[-1]}

    # Query the DB for each Key
    for key in race_data:
        c.execute('''SELECT raceID FROM races WHERE raceID = ?''', (key,))
        db_race = c.fetchone()

        if db_race == None:
            print("Should Join raceID: {}".format(key))
            # if Key Not in DB, fire off the Join function.
            # Once successfully joined. Add it to the DB.
        else:
            print("raceID {} already Joined".format(key))


def login():
    login_url = '{}{}'.format(config.get('multiGP', 'url'), config.get('multiGP', 'login_uri'))
    login_info = {'LoginForm[username]': config.get('multiGP', 'username'),
                  'LoginForm[password]': config.get('multiGP', 'password'),
                  'yt0': 'Log in'
                  }

    response = requests.post(login_url, data=login_info, allow_redirects=False)
    session.cookies = response.cookies

    return session


def click_join(session):
    # Dig out the race ID from the URI

    # Plug the Race ID into the join URI.
    # Add the aircraft ID to the Data
    # send the post.


    event_page = 'http://www.multigp.com/races/view/6443/Whoop-Whoop'
    join_page = 'http://www.multigp.com/races/join/6443'
    # test_cookie =
    form_data = {'RaceEntry[aircraftId]': '16205'}
    test = session.post(join_page, data=form_data)
    # pass

    print test.status_code


def create_db():
    # This will Create the database and then read the rss feed and input all the existing races into the database.
    print('Running first time db setup.')
    with open('./races.db', 'ab'):
        pass
    # Connect to the database
    conn = sqlite3.connect('./races.db')
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE races (raceID, title, link, pubDate, description, raceDate)''')
    conn.commit()

    # read rss feed
    races_responce = session.get(rss_url).content

    # convert to something useful
    races_responce = xmltodict.parse(races_responce, process_namespaces=True)

    race_data = []
    for race in races_responce['rss']['channel']['item']:
        current = []
        # Dig out the Race ID from the URL.
        current.append(race['link'].split('/')[5])
        # current.append(raceID)
        current.append(race['title'])
        current.append(race['link'])
        current.append(race['pubDate'])
        current.append(race['description'])
        current.append(race['title'].split('-')[-1])
        current = tuple(current)
        race_data.append(current)

    c.executemany(''' INSERT INTO races(raceID, title, link, pubDate, description, raceDate) VALUES(?,?,?,?,?,?)''', race_data)
    conn.commit()


def start_up():
    # stuff to run at start up. Does basic check like if the DB has been created or not. If not then create it.
    if not os.path.exists('./races.db'):
        create_db()


def test():
    conn = sqlite3.connect('./races.db')
    c = conn.cursor()
    c.execute('''SELECT raceID FROM races''')
    raw_races = c.fetchall()

    races = []
    for thing in raw_races:
        races.append(thing[0])
    if '6532' in races:
        print 'yes'

    print test


if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')
    rss_url = '{}{}'.format(config.get('multiGP', 'url'), config.get('chapter', 'rss_uri'))

    # Flag for if there is a new race not already in the history DB.
    new_race = False

    #setting up the session
    session = requests.Session()
    start_up()

    conn = sqlite3.connect('./races.db')
    c = conn.cursor()

    watch_rss()
    # test()
    # No need to login at this point. You can access this page un authenticated
    # watch_rss(rss_url)

    # if new_race:
    #     login()
    #     click_join()
