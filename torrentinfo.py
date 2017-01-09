"""
torrentinfo.py - Sopel module to fetch torrent information for links sent to channels
"""

from sopel import module
import bleach
import requests
from lxml import etree

NYAA_URL = 'https://www.nyaa.se/?page=view&tid=%s'


@module.rule('.*https?:\/\/(?:www\.)?nyaa.(?:se|eu)\/\S*(?:\?|&)tid=(\d+).*')
def nyaa_info(bot, trigger):
    try:
        r = requests.get(url=NYAA_URL % trigger.group(1), timeout=(10.0, 4.0))
    except requests.exceptions.ConnectTimeout:
        bot.say("Connection timed out.")
    except requests.exceptions.ConnectionError:
        bot.say("Couldn't connect to server.")
    except requests.exceptions.ReadTimeout:
        bot.say("Server took too long to send data.")
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        bot.say("HTTP error: " + e.message)

    page = etree.HTML(r.content)

    t = {}

    t['name'] = page.cssselect('td.viewtorrentname')[0]
    t['size'] = page.cssselect('#main > div.content > div > table.viewtable > tbody > tr:nth-child(6) > td.vtop')[0]

    for key in t.keys():
        t[key] = bleach.clean(etree.tostring(t[key]), tags=[], strip=True)

    bot.say("[Nyaa] {name} | Size: {size}".format(name=t['name'], size=t['size']))
