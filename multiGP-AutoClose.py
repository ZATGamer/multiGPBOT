#!/usr/bin/python
import ConfigParser
import bs4, requests


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


if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')

    res = requests.get('http://www.multigp.com/races/view/{}/'.format(config.get('auto_close', 'id')))
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    count = len(soup.select('.list-view .row'))

    session = requests.Session()

    print('Race currently has {} pilots. Out of {}'.format(count, config.get('auto_close', 'pilots')))

    if count == int(config.get('auto_close', 'pilots')):
        login()
        close_race()




# __cfduid=de3b087f85518dffc35c39cb1d455ea841485459160; 74cbf1dfba8d0d29eea3efdf9b88e618=60838e136d1c7ce38d69199ee58239b94a702be2s%3A116%3A%22e9eb205a9494eed8190f96909e4f92031afe11a9a%3A4%3A%7Bi%3A0%3Bs%3A4%3A%221722%22%3Bi%3A1%3Bs%3A19%3A%22zatgaming%40gmail.com%22%3Bi%3A2%3Bi%3A2592000%3Bi%3A3%3Ba%3A0%3A%7B%7D%7D%22%3B; JSESSIONID=h2hfbqjmrggb4m0s9u4suenf4f9mkv8u0emjqbt3ptpt5f2ksv9tpk67q50imavat47qkan05a01tcu6fdjps4gqk14300io5qk19s0; __unam=c3bc5ec-159dc440224-2d8a0d-438; _ga=GA1.2.50950696.1485459164; _gid=GA1.2.1845621608.1499268883; _gat=1
# __cfduid=de3b087f85518dffc35c39cb1d455ea841485459160; 74cbf1dfba8d0d29eea3efdf9b88e618=60838e136d1c7ce38d69199ee58239b94a702be2s%3A116%3A%22e9eb205a9494eed8190f96909e4f92031afe11a9a%3A4%3A%7Bi%3A0%3Bs%3A4%3A%221722%22%3Bi%3A1%3Bs%3A19%3A%22zatgaming%40gmail.com%22%3Bi%3A2%3Bi%3A2592000%3Bi%3A3%3Ba%3A0%3A%7B%7D%7D%22%3B; JSESSIONID=h2hfbqjmrggb4m0s9u4suenf4f9mkv8u0emjqbt3ptpt5f2ksv9tpk67q50imavat47qkan05a01tcu6fdjps4gqk14300io5qk19s0; __unam=c3bc5ec-159dc440224-2d8a0d-438; _ga=GA1.2.50950696.1485459164; _gid=GA1.2.1845621608.1499268883