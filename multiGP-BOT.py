#!/usr/bin/python

import requests
import xmltodict


def main(url):
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
    login_url = 'http://www.multigp.com/user/site/login/'
    login_info = {'LoginForm[username]': 'xxx',
                  'LoginForm[password]': 'xxx',
                  'yt0': 'Log in'
                  }

    response = requests.post(login_url, data=login_info)
    print response.status_code
    return response


def click_join(cookies):
    event_page = 'http://www.multigp.com/races/view/6443/Whoop-Whoop'
    join_page = 'http://www.multigp.com/races/join/6443'
    # test_cookie =
    form_data = {'RaceEntry[aircraftId]': '16205'}
    cookie = {'JSESSIONID': 'nd4hv1b8onfq0s9lmuvn67o65vjhtaadc02s4o6qfk6r58nq2jeqakutqu3auqmgsqc5a14e6tksk25o6s4sgo4bnhe4aeulk45kqg3',
              '03a98afcad68e32d5df5dd91fcf33bae': 'a0b91be0f29ca8804bde7eedff7c97c48417c435s%3A116%3A%22c5f7e3e4de32051fe09f738376f9f8b36adb0c46a%3A4%3A%7Bi%3A0%3Bs%3A4%3A%221722%22%3Bi%3A1%3Bs%3A19%3A%22zatgaming%40gmail.com%22%3Bi%3A2%3Bi%3A2592000%3Bi%3A3%3Ba%3A0%3A%7B%7D%7D%22%3B'}
    # for c in cookies.cookies:
    #     print(c.name, c.value)
    test = requests.post(join_page, cookies=cookie, data=form_data)
    # pass

    print test.status_code



if __name__ == '__main__':
    url = 'http://www.multigp.com/multigp/chapter/rss/name/AuroraFPV'
    # main(url)
    r1 = login()
    r2 = click_join(r1)
