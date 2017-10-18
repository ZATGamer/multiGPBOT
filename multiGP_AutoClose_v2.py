#!/usr/bin/python

import ConfigParser
import bs4, requests
import os
import datetime
import message_groupme
import sqlite3
import groupme_BOT


def send_close_notice(count):
    print("Race has Reached Limit ({} Pilots). CLOSE IT!".format(count))
    if not notified:
        print("Sending Notice")
        body = 'Time to close the race!\n' \
               '{}\n' \
               'Has {} out of {} Pilots.\n ' \
               'Close URL: "http://www.multigp.com/mgp/multigp/race/close/id/{}"'.format(title, count, max_pilots, raceID)
        send_notice(body)
        c.execute('''UPDATE races SET notified=? WHERE raceID=?''', (True, raceID))
        conn.commit()

    else:
        print("Already notified.")


def close_race(notified, attempt, raceID, closeurl):
    print("Logging In.")
    login()

    print("Closing the Race")
    test = session.get(closeurl)
    print test.status_code
    attempt += 1
    if not notified:
        body = 'I am Closing the Race {}.'.format(raceID)
        send_notice(body)
        c.execute('''UPDATE races SET notified=? WHERE raceID=?''', (True, raceID))

    c.execute('''UPDATE races SET attempt=? WHERE raceID=?''', (attempt, raceID))
    conn.commit()
    return attempt


def check_race(soup, raceID, max_pilots, old_count):

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
    body = "Race {} has been closed.\n" \
           "(Either someone pressed the link or Auto Close worked.)".format(raceID)
    send_notice(body)


def get_name(soup, raceID):
    print('Getting the name of the race {}.'.format(raceID))

    race_name = soup.select_one('h1').getText()
    race_name = race_name.strip()
    race_name = race_name.split('\n')
    race_name = race_name[0]

    return race_name


def update_name(race_name, raceID):
    print('Updating the name for Race {}.'.format(raceID))

    c.execute('''UPDATE races SET title=? WHERE raceID=?''', (race_name, raceID))
    conn.commit()


def update_status(soup, raceID, closed):
    if closed is None:
        print('updating closed')
        c.execute('''UPDATE races SET closed=? WHERE raceID=?''', (False, raceID))
        conn.commit()

    status = soup.select_one('.fixed').getText()
    status = status.strip().lower()

    if status == 'closed':
        print("Site shows race as closed.")
        if not closed:
            print("Not closed in the DB but closed on the site Updating it.")
            c.execute('''UPDATE races SET closed=? WHERE raceID=?''', (True, raceID))
            conn.commit()

        print("Race Closed")

    else:
        if closed:
            print("Closed in the DB but not on the site Updating it.")
            c.execute('''UPDATE races SET closed=? WHERE raceID=?''', (False, raceID))
            # Race reopened, reset the attempt count.
            c.execute('''UPDATE races SET attempt=? WHERE raceID=?''', (0, raceID))
            conn.commit()

        print("Race Still Open")


def is_closed(soup):
    status = soup.select_one('.fixed').getText()
    status = status.strip().lower()

    if status == 'closed':
        print("Race Closed")
        return True
    else:
        print("Race Still Open")
        return False


def send_notice(body):
    # email_notification.send_notification(subject, body)
    message_groupme.send_message(body)


def login():
    login_url = '{}{}'.format(config.get('multiGP', 'url'), config.get('multiGP', 'login_uri'))
    login_info = {'LoginForm[username]': config.get('multiGP', 'username'),
                  'LoginForm[password]': config.get('multiGP', 'password'),
                  'yt0': 'Log in'
                  }

    response = requests.post(login_url, data=login_info, allow_redirects=False, verify=False)
    session.cookies = response.cookies


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
                                        title, date, closed, url, attempt, closed_notified)''')
    db_conn.commit()


def start_up():
    # stuff to run at start up. Does basic check like if the DB has been created or not. If not then create it.
    if not os.path.exists(config.get('database', 'auto_close')):
        create_db()


def watch_for_new_race(soup):
    # Read in all the races.

    table = soup.select('.grid-view table tbody tr')
    for race in table:
        race_data = race.select('td')
        # Parse out all the dates
        date = str(race_data[0])[4:-5]
        date = datetime.datetime.strptime(date, '%b %d, %Y')
        # Dig out RaceID's
        raceID = str(race_data[1])[12:-9].split('/')[7][6:]
        race_name = str(race_data[1]).split('>')[2][:-3]

        # Look for races in the future
        if datetime.datetime.now() < date:
            print("Race {} is in the future".format(raceID))
            # Check DB to see if already watching race.
            c.execute('''SELECT * FROM races WHERE raceID=?''', (raceID,))
            i_check = c.fetchone()
            if not i_check:
                print("Not Watching Race.")
                print("Adding {} to Watch list.".format(raceID))
                # If NOT in DB, Add it with a pilot count of 24
                groupme_BOT.add_race_watch(raceID, 24)


def get_soup(url):
    res = session.get(url, verify=False)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    return soup


if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')

    start_up()

    db_path = config.get('database', 'auto_close')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''SELECT * FROM races''')
    races = c.fetchall()

    session = requests.Session()

    if races:
        for race in races:
            raceID = race[0]
            max_pilots = race[1]
            notified = race[2]
            old_count = race[3]
            title = race[4]
            date = datetime.datetime.strptime(race[5], '%Y-%m-%d %H:%M:%S')
            closed = race[6]
            attempt = race[8]
            if attempt is None:
                attempt = int(0)
            else:
                attempt = int(attempt)

            view_url = "{}{}{}/".format(config.get('multiGP', 'url'), config.get('multiGP', 'view_uri'), raceID)
            close_url = "{}{}{}/".format(config.get('multiGP', 'url'), config.get('multiGP', 'close_uri'), raceID)
            login_url = "{}{}".format(config.get('multiGP', 'url'), config.get('multiGP', 'login_uri'))

            view_soup = get_soup(view_url)

            r_name = get_name(view_soup, raceID)
            if r_name != title:
                update_name(r_name, raceID)

            if not closed:
                count = check_race(view_soup, raceID, max_pilots, old_count)

                if closed is None:
                    update_status(view_soup, raceID, closed)

                if count >= max_pilots:
                    # We should close the race[
                    attempt = close_race(notified, attempt, raceID, close_url)
                    view_soup = get_soup(view_url)
                    update_status(view_soup, raceID, closed)

                elif datetime.datetime.now() > date:
                    attempt = close_race(notified, attempt, raceID, close_url)
                    view_soup = get_soup(view_url)
                    update_status(view_soup, raceID, closed)

                if attempt == 2 and count >= max_pilots:
                    print ("Send attempt notice")
                    body = 'I am having troubles closing {}! Please manually close\n' \
                           '{}'.format(raceID, close_url)
                    send_notice(body)

                elif attempt == 2 and datetime.datetime.now() > date:
                    body = 'Race {} Date has passed. I have tried to close the race but am having issues.\n' \
                           'Please close it manually.\n' \
                           '{}'.format(raceID, close_url)
                    send_notice(body)
            else:
                if not is_closed(view_soup) and closed:
                    # Closed in DB but not on the site. (means someone opened the race back up)
                    print("Looks like the race was reopened.")
                    update_status(view_soup, raceID, closed)

                if datetime.datetime.now() > date:
                    stop_watching(raceID)

    else:
        print("No Races to check.")

    # Checking to see if we need to add a Race to the watch list.
    chapter_view_url = "{}{}".format(config.get('multiGP', 'url'), config.get('chapter', 'view_uri'))
    chapter_view_soup = get_soup(chapter_view_url)

    watch_for_new_race(chapter_view_soup)

    conn.close()
