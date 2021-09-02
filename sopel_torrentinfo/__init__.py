# coding=utf-8
"""
torrentinfo - Sopel plugin to fetch info for torrent links
"""

from lxml import etree
import requests

from sopel import plugin


NYAA_URL = 'https://nyaa.si/view/%s'


@plugin.url(r'https?:\/\/(?:www\.)?nyaa\.si\/(?:view|download)\/(\d+)')
def nyaa_info(bot, trigger, match=None):
    parsed_url = NYAA_URL % match.group(1)
    try:
        r = requests.get(url=parsed_url, timeout=(10.0, 4.0))
    except requests.exceptions.ConnectTimeout:
        return bot.say("[Nyaa] Connection timed out.")
    except requests.exceptions.ConnectionError:
        return bot.say("[Nyaa] Couldn't connect to server.")
    except requests.exceptions.ReadTimeout:
        return bot.say("[Nyaa] Server took too long to send data.")
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return bot.say("[Nyaa] HTTP error: " + str(e))

    page = etree.HTML(r.content)

    t = {}

    t['name'] = page.cssselect('meta[property="og:title"]')[0].get('content').replace(' :: Nyaa', '')
    t['category'] = page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 1)[0]
    t['size'] = page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 2)[1]
    t['uploader'] = page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 3)[2]
    t['link'] = parsed_url
    for key in t.keys():
        t[key] = (' '.join(t[key].split()))
    bot.say("[Nyaa] Name: {name} | {category} | Size: {size} | {uploader}".format(**t))
