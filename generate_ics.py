#!/usr/bin/python

import time
import bs4, requests
import datetime
import urllib2
from ics import Calendar, Event
import os.path


def get_date_time(soup):
    # Digging out the Date/Time
    raw_date = soup.find(itemprop="startDate").getText()
    raw_time = soup.select_one('.text-center small').getText()
    raw_time = raw_time.split()
    date_time = "{} {} {}".format(raw_date, raw_time[1], raw_time[2])
    date_time = datetime.datetime.strptime(date_time, '%b %d, %Y %I:%M:%S %p')

    if time.localtime().tm_isdst:
        date_time = date_time - datetime.timedelta(hours=-6)
        # -6
    else:
        date_time = date_time - datetime.timedelta(hours=-7)
        # -7

    return date_time


def get_race_name(soup):
    race_name = soup.select_one('h1').getText()
    race_name = race_name.strip()
    race_name = race_name.split('\n')
    race_name = race_name[0]
    return race_name


def get_address(soup):
    raw_address = soup.find(itemprop="location").contents[1].get('href')
    raw_address = raw_address.split('/')
    raw_address = urllib2.unquote(raw_address[4])
    raw_address = raw_address.split('+')

    address = ''
    for item in raw_address[1:]:
        address += "{} ".format(item)

    return address


def build_ics(raceID, date_time, race_name, address):
    c = Calendar()
    e = Event()
    e.name = race_name
    e.location = address
    e.begin = date_time
    e.end = date_time + datetime.timedelta(hours=4)

    c.events.append(e)
    with open('./ics/{}.ics'.format(raceID), 'w') as my_file:
        my_file.writelines(c)


def get_soup(raceID):
    print('Retrieving the webpage.'.format(raceID))

    res = requests.get('http://www.multigp.com/mgp/races/view/{}/'.format(raceID), verify=False)

    # Parsing the Page.
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    return soup


def generate_ics(raceID):
    if os.path.isfile('./ics/{}.ics'.format(raceID)):
        print "yes"
        return 0
    else:
        print "Nope, Creating"
        soup = get_soup(raceID)
        date_time = get_date_time(soup)
        race_name = get_race_name(soup)
        address = get_address(soup)
        build_ics(raceID, date_time, race_name, address)
        return 0


if __name__ == '__main__':
    # raceID = 10486
    # soup = get_soup(raceID)
    # date_time = get_date_time(soup)
    # race_name = get_race_name(soup)
    # address = get_address(soup)
    # build_ics()
    generate_ics(10486)
