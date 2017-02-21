#!/usr/bin/python

import os
import requests
import xmltodict
import sqlite3
import ConfigParser


def watch_rss(url):
    # This function will watch the RSS for changes and then will set the change flag to true when it sees them
    responce = requests.get('http://www.multigp.com/multigp/chapter/rss/name/AuroraFPV').content

    races_responce = xmltodict.parse(responce, process_namespaces=True)

    races = []

    for race in races_responce['rss']['channel']['item']:
        current = []
        current.append(race['pubDate'])
        current.append(race['link'])
        print race['pubDate']
        print race['link']
        races.append(current)

    print len(races)


def test():
    test_url = 'http://www.multigp.com/multigp/aircraft/update/id/16205'
    test = requests.get(test_url)
    print test.status_code


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
    with open('./races.db'):
        pass
    # Connect to the database
    conn = sqlite3.connect('./races.db')
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE races (title, link, pubDate, description)''')
    conn.commit()

    # read rss feed
    races_responce = session.get(rss_url).content

    # convert to something useful
    races_responce = xmltodict.parse(races_responce, process_namespaces=True)

    race_data = []
    for race in races_responce['rss']['channel']['item']:
        current = []
        # Dig out the Race ID from the URL.
        # raceID = race['link'].split('/')
        current.append(raceID)
        current.append(race['title'])
        current.append(race['link'])
        current.append(race['pubDate'])
        current.append(race['description'])


def start_up():
    # stuff to run at start up. Does basic check like if the DB has been created or not. If not then create it.
    if not os.path.exists('./races.db'):
        create_db()


if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')
    rss_url = config.get('chapter', 'url')

    # Flag for if there is a new race not already in the history DB.
    new_race = False

    #setting up the session
    session = requests.Session()

    # No need to log in at this point. You can access this page un authenticated
    watch_rss(rss_url)

    # if new_race:
    #     login()
    #     click_join()
