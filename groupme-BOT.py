import requests
import ConfigParser
from flask import Flask, request
import sqlite3

app = Flask(__name__)


@app.route('/', methods=['POST'])
def web_hook():
    data = request.get_json()
    called = ''

    # make sure I didn't send the message
    if data['name'] != 'Race Full Notice':
        message = data['text'].split(' ')
        if message[0].lower() == '!bot':
            # You have asked the bot to do something. Now do what it asks.
            if message[1].lower() == 'add':
                called = 'add'
                add_race_watch()

            elif message[1].lower() == 'remove':
                called = 'remove'
                remove_race_watch()

            elif message[1].lower() == 'update':
                called = 'update'
                update_race_watch()

            elif message[1].lower() == 'list':
                called = 'list'
                list_race_watch()

            elif message[1].lower() == 'status':
                called = 'status'
                get_pilot_count()

            else:
                called = 'help'
                help_info()

    return called, 200


def help_info():
    # This will send a message with what I can do.
    print 'help'
    message = '!bot help --\n' \
              'I can do the following things.\n' \
              '!bot add <raceID> <maxPilots> -- Add a race to the auto close Notify list.\n' \
              '!bot update <raceID> <maxPilots> -- Updates the specified race\'s maxPilots\n' \
              '!bot remove <raceID> -- Removes the specified race from the watch list.\n ' \
              '!bot list -- Lists all races currently being watched by me.\n' \
              '!bot status <raceID> -- Gets the current pilot count for specified race.'
    send_message(message)


def get_pilot_count():
    # Get the current pilot count for raceID
    pass


def list_race_watch():
    # list all races currently being watched.
    conn, c = get_db_conn()
    c.execute('''SELECT * FROM races''')
    races = c.fetchall()
    m_body = 'Currently Watching:\n'
    for race in races:
        m_body += 'RaceId: {}, Max Pilots: {}.\n'.format(race[0], race[1])

    send_message(m_body)

    conn.close()


def update_race_watch():
    # This will update a race already being watched.
    return 'update'


def add_race_watch():
    # This will add a race to the watch list.
    return 'add'


def remove_race_watch():
    # This will remove a race from the watch list.
    return 'remove'


def send_message(body):
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')

    url = config.get('GroupMe', 'api_url')
    bot_id = config.get('GroupMe', 'test_bot_id')

    data = {"text": body, "bot_id": bot_id}

    session = requests.session()
    session.verify = False

    session.post(url, data=data)


def get_db_conn():
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')
    db_path = config.get('database', 'auto_close')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    return conn, c


if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')

    bot_id = config.get('GroupMe', 'bot_id')

    test = {"text": "Sorry for the spam", "bot_id": bot_id}

    url = 'https://api.groupme.com/v3/messages'
    print url

    s = requests.Session()
    # s.headers.update({'token': token})
    s.headers.update({'Accept': 'application/json'})
    s.verify = False
    s.headers.update({'token': bot_id})
    # r_data = s.post(url, data=test)
    r_data = s.get(url)
    print r_data.content
