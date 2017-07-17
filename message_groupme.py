import requests
import ConfigParser


def send_message(body):
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')

    url = config.get('GroupMe', 'api_url')
    bot_id = config.get('GroupMe', 'bot_id')

    data = {"text": body, "bot_id": bot_id}

    session = requests.session()
    session.verify = False

    session.post(url, data=data)


if __name__ == '__main__':
    token = ''

    test = {"text": "Sorry for the spam", "bot_id": "xxxx"}

    url = 'https://api.groupme.com/v3/bots/post'
    print url

    s = requests.Session()
    # s.headers.update({'token': token})
    s.headers.update({'Accept': 'application/json'})
    s.verify = False
    # r_data = s.post(url, data=test)
    r_data = s.post(url, data=test)
    print r_data.content
