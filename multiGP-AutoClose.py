#!/usr/bin/python
import ConfigParser
import bs4, requests
import os.path
import email_notification


def login():
    login_url = '{}{}'.format(config.get('multiGP', 'url'), config.get('multiGP', 'login_uri'))
    login_info = {'LoginForm[username]': config.get('multiGP', 'username'),
                  'LoginForm[password]': config.get('multiGP', 'password'),
                  'yt0': 'Log in'
                  }

    response = requests.post(login_url, data=login_info, allow_redirects=False)
    session.cookies = response.cookies


def close_race():
    close_url = ''
    # close_url = 'http://www.multigp.com/multigp/race/close/id/9369'
    # print(close_url)
    # close_race_code = session.post(close_url)
    # close_race_code = session.get(close_url)

    # update_race_data = session.get('http://www.multigp.com/multigp/race/updateRaceEntries/id/9369')

    # print("Race CLOSED status code: {}".format(close_race_code.status_code))
    print("Race has Reached Limit. CLOSE IT!")
    if not os.path.exists('notified.txt'):
        print("Sending Notice")
        body = 'Time to close the race!\n Close URL: "http://www.multigp.com/multigp/race/close/id/{}"'.format(config.get('auto_close', 'id'))
        email_notification.send_notification("CLOSE THE RACE!", body)
        with open('notified.txt', 'ab'):
            pass
    else:
        print("Already notified.")


if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')

    res = requests.get('http://www.multigp.com/races/view/{}/'.format(config.get('auto_close', 'id')))
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    count = len(soup.select('.list-view .row'))

    session = requests.Session()

    print('Race currently has {} pilots. Out of {}'.format(count, config.get('auto_close', 'pilots')))

    if count >= int(config.get('auto_close', 'pilots')):
        login()
        close_race()
