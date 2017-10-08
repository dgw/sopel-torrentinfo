"""
torrentinfo.py - Sopel module to fetch torrent information for links sent to channels
"""

from sopel import module
import requests
import lxml
from lxml import etree
import re
import bleach

NYAA_URL = 'https://nyaa.si/view/%s'
ANIDEX_URL = 'https://anidex.info/torrent/%s'

@module.rule('.*https?:\/\/(?:www\.)?nyaa\.si\/(?:view|download)\/(\d+).*')
def nyaa_info(bot, trigger):
    parsed_url = NYAA_URL % trigger.group(1)
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
        return bot.say("[Nyaa] HTTP error: " + e.message)

    page = etree.HTML(r.content)

    t = {}

    t['name'] = page.cssselect('meta[property="og:title"]')[0].get('content').replace(' :: Nyaa', '').encode('utf-8')
    t['category'] = page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 1)[0]
    t['size'] = page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 2)[1]
    t['uploader'] = page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 3)[2]
    t['link'] = parsed_url

    bot.say("[Nyaa] Name: {name} | {category}| Size:{size}|{uploader} | {link}".format(**t))

@module.rule('.*https?:\/\/(?:www\.)?anidex\.(?:info|moe)\/(?:torrent|dl)\/(\d+).*')
def anidex_info(bot, trigger):
    parsed_url = ANIDEX_URL % trigger.group(1)
    try:
        r = requests.get(url=parsed_url, timeout=(10.0, 4.0))
    except requests.exceptions.ConnectTimeout:
        return bot.say("[Anidex] Connection timed out.")
    except requests.exceptions.ConnectionError:
        return bot.say("[Anidex] Couldn't connect to server.")
    except requests.exceptions.ReadTimeout:
        return bot.say("[Anidex] Server took too long to send data.")
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return bot.say("[Anidex] HTTP error: " + e.message)

    page = etree.HTML(r.content)

    t = {}

    t['name'] = page.cssselect('#content > div.panel.panel-default > div > h3')[0]
    t['size'] = page.cssselect('#scrape_info_table > tbody > tr:nth-child(2) > td')[0]
    t['uploader'] = page.cssselect('#edit_torrent_form > div.row > div:nth-child(1) > table:nth-child(1) > tbody > tr:nth-child(1) > td > a')[0]
    for key in t.keys():
        t[key] = bleach.clean(etree.tostring(t[key]), tags=[], strip=True)
    t['link'] = parsed_url
    t['name'] = re.sub(r'\ \+(\d)+', '', t['name'])

    bot.say("[Anidex] Name:{name}| Size:{size}| Uploaded by: {uploader} | {link}".format(**t))
