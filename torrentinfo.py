"""
torrentinfo.py - Sopel module to fetch torrent information for links sent to channels
"""

# -*- coding: utf-8 -*-
# encoding=utf8  
import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')

from sopel import module
import requests
from lxml import etree
from pyquery import PyQuery
import re

NYAA_URL = 'https://nyaa.si/view/%s'
ANIDEX_URL = 'https://anidex.info/torrent/%s'

@module.rule('.*https?:\/\/(?:www\.)?nyaa\.si\/(?:view|download)\/(\d+).*')
#@module.rule('.*https?:\/\/(?:www\.)?nyaa.(?:se|eu)\/\S*(?:\?|&)tid=(\d+).*')
def nyaa_info(bot, trigger):
    try:
        r = requests.get(url=NYAA_URL % trigger.group(1), timeout=(10.0, 4.0))
    except requests.exceptions.ConnectTimeout:
        #bot.say("Connection timed out.")
        return
    except requests.exceptions.ConnectionError:
        #bot.say("Couldn't connect to server.")
        return
    except requests.exceptions.ReadTimeout:
        #bot.say("Server took too long to send data.")
        return
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        #bot.say("HTTP error: " + e.message)
        bot.msg('#katou-test', 'Nyaa resolving failed for URL: '+NYAA_URL % trigger.group(1)+' at channel '+trigger.sender+' triggered by '+trigger.nick)
        return bot.say("[Nyaa] Torrent not found!")

    page = etree.HTML(r.content)
    pq = PyQuery(page)

    t = {}

    t['name'] = pq('body > div > div:nth-child(1) > div.panel-heading > h3')
    t['size'] = pq('body > div > div:nth-child(1) > div.panel-body > div:nth-child(4) > div:nth-child(2)')
    t['uploader'] = pq('body > div > div:nth-child(1) > div.panel-body > div:nth-child(2) > div:nth-child(2) > a')
    t['link'] = NYAA_URL % trigger.group(1)
    t['name'] = t['name'].text()
    t['size'] = t['size'].text()
    t['uploader'] = t['uploader'].text()

    bot.say("[Nyaa] Name: {name} | Size: {size} | Uploaded by: {uploader} | {link}".format(name=t['name'], size=t['size'], uploader=t['uploader'], link=t['link']))

@module.rule('.*https?:\/\/(?:www\.)?anidex\.(?:info|moe)\/(?:torrent|dl)\/(\d+).*')
def anidex_info(bot, trigger):
    try:
        r = requests.get(url=ANIDEX_URL % trigger.group(1), timeout=(10.0, 4.0))
    except requests.exceptions.ConnectTimeout:
        bot.say("[Anidex] Connection timed out.")
        return
    except requests.exceptions.ConnectionError:
        bot.say("[Anidex] Couldn't connect to server.")
        return
    except requests.exceptions.ReadTimeout:
        bot.say("[Anidex] Server took too long to send data.")
        return
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        #bot.say("HTTP error: " + e.message)
        bot.msg('#katou-test', 'Anidex resolving failed for URL: '+NYAA_URL % trigger.group(1)+' at channel '+trigger.sender+' triggered by '+trigger.nick)
        return bot.say("[Anidex] Torrent not found!")

    page = etree.HTML(r.content)
    pq = PyQuery(page)

    t = {}

    t['name'] = pq('#content > div.panel.panel-default > div > h3')
    t['size'] = pq('#scrape_info_table > tbody > tr:nth-child(2) > td')
    t['uploader'] = pq('#edit_torrent_form > div.row > div:nth-child(1) > table:nth-child(1) > tbody > tr:nth-child(1) > td > a')
    t['link'] = ANIDEX_URL % trigger.group(1)
    t['name'] = t['name'].text()
    t['name'] = re.sub('\ \+(\d)+', '', t['name'])
    t['size'] = t['size'].text()
    t['uploader'] = t['uploader'].text()

    bot.say("[Anidex] Name: {name} | Size: {size} | Uploaded by: {uploader} | {link}".format(name=t['name'], size=t['size'], uploader=t['uploader'], link=t['link']))

