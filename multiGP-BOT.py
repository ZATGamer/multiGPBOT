#!/usr/bin/python

import os
import requests
import xmltodict
import sqlite3
import ConfigParser
import datetime


def watch_rss(new_race):
    # Do a GET on the site for the RSS
    raw_race_data = session.get(rss_url).content

    # Convert the XML to something I can use
    races_response = xmltodict.parse(raw_race_data, process_namespaces=True)

    # Create a Dict of all the data using the RaceID as the Key
    race_data = {}
    for race in races_response['rss']['channel']['item']:
        race_data[race['link'].split('/')[5]] = {'title': race['title'],
                                                 'link': race['link'],
                                                 'pubDate': race['pubDate'],
                                                 'description': race['description'],
                                                 'raceDate': race['title'].split('-')[-1]}

    # Query the DB for each Key
    for key in race_data:
        c.execute('''SELECT raceID FROM races WHERE raceID = ?''', (key,))
        db_race = c.fetchone()

        if not db_race:
            # if Key Not in DB, fire off the Join function.
            print("Race available to join raceID: {}".format(key))
            new_race = True
            joined = join_race(key, race_data[key])
            # Once successfully joined. Add it to the DB.
            if joined:
                add_race_to_db(key, race_data[key])
            else:
                print("Something went wrong, Race {} not joined or added to DB.".format(key))
    return new_race


def join_race(key, race_data):
    # Check to see if race is in blackout
    in_blackout = check_blackout(race_data)

    if not in_blackout:
        # If not in blackout: Join...
        # Log into multiGP
        login()

        # Send Post to join the race with specified quad.
        join_status = click_join(key)

        if join_status == 200:
            # Once Joined return True so I know it worked.
            return True
        else:
            return False

    else:
        # else don't join but add to DB.
        return True


def check_blackout(race_data):
    # read in blackout dates from config.
    # Get date when race is.
    race_date = datetime.datetime.strptime(race_data['raceDate'], " %b %d, %Y")
    bo_dates = config.get('blackout', 'dates').split(',')
    bo_dates_parsed = []
    for date in bo_dates:
        bo_dates_parsed.append(datetime.datetime.strptime(date, '%Y%m%d'))
    if race_date in bo_dates_parsed:
        print("Race date is in blackout dates.")
        return True
    else:
        print("Race date is NOT in blackout dates.")
        return False


def login():
    login_url = '{}{}'.format(config.get('multiGP', 'url'), config.get('multiGP', 'login_uri'))
    login_info = {'LoginForm[username]': config.get('multiGP', 'username'),
                  'LoginForm[password]': config.get('multiGP', 'password'),
                  'yt0': 'Log in'
                  }

    response = requests.post(login_url, data=login_info, allow_redirects=False)
    session.cookies = response.cookies


def click_join(race_id):
    # Build the join URL via config and plug in the raceID.
    join_url = '{}{}{}'.format(config.get('multiGP', 'url'), config.get('multiGP', 'join_uri'), race_id)

    # Printing URL for Console Debugging.
    print(join_url)

    # Build the form data
    aircraft_data = {'RaceEntry[aircraftId]': config.get('chapter', 'aircraft_id')}

    # Printing data for Console Debugging.
    print aircraft_data

    # using the session send the post.
    join_post = session.post(join_url, data=aircraft_data)
    # pass

    # More debugging stuff.
    print("Join POST status code: {}".format(join_post.status_code))

    return join_post.status_code


def add_race_to_db(race_id, race_data):
    # Prep the data for the DB
    insert_data = (race_id, race_data['title'], race_data['link'], race_data['pubDate'], race_data['description'],
                   race_data['raceDate'])
    c.execute('''INSERT INTO races(raceID, title, link, pubDate, description, raceDate) VALUES(?,?,?,?,?,?)''',
              insert_data)
    conn.commit()


def create_db():
    # This will Create the database and then read the rss feed and input all the existing races into the database.
    print('Running first time db setup.')
    db_path = config.get('database', 'path')
    with open(db_path, 'ab'):
        pass
    # Connect to the database
    db_conn = sqlite3.connect(db_path)
    db_c = db_conn.cursor()
    # Create table
    db_c.execute('''CREATE TABLE races (raceID, title, link, pubDate, description, raceDate)''')
    db_conn.commit()

    # read rss feed
    races_response = session.get(rss_url).content

    # convert to something useful
    races_response = xmltodict.parse(races_response, process_namespaces=True)

    race_data = []
    for race in races_response['rss']['channel']['item']:
        current = (
            # Dig out the Race ID from the URL.
            race['link'].split('/')[5],
            # current.append(raceID)
            race['title'],
            race['link'],
            race['pubDate'],
            race['description'],
            race['title'].split('-')[-1]
        )
        race_data.append(current)

    db_c.executemany('''INSERT INTO races(raceID, title, link, pubDate, description, raceDate) VALUES(?,?,?,?,?,?)''',
                     race_data)
    db_conn.commit()
    db_conn.close()


def start_up():
    # stuff to run at start up. Does basic check like if the DB has been created or not. If not then create it.
    if not os.path.exists(config.get('database', 'path')):
        create_db()


if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')
    rss_url = '{}{}'.format(config.get('multiGP', 'url'), config.get('chapter', 'rss_uri'))

    # setting up the session
    session = requests.Session()
    start_up()

    # Setting up the DB connection
    db_path = config.get('database', 'path')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Flag for if there is a new race not already in the history DB.
    new_race = False

    # Start the watch.
    new_race = watch_rss(new_race)

    # Be nice the DB and close the connection
    conn.close()

    if new_race:
        print("{} New Race".format(datetime.datetime.now()))
    else:
        print("{} No New Race".format(datetime.datetime.now()))
