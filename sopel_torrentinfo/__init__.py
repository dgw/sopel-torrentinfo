# coding=utf-8
"""
torrentinfo - Sopel plugin to fetch info for torrent links
"""

import pkg_resources

import requests

from sopel import plugin, tools


def setup(bot):
    global patterns

    bot.memory['torrentinfo_providers'] = tools.SopelMemory()

    entry_points = pkg_resources.iter_entry_points('sopel_torrentinfo.providers')
    patterns = []

    for entry_point in entry_points:
        provider = bot.memory['torrentinfo_providers'][entry_point.name] = entry_point.load()
        patterns.append(provider.link_pattern())


def lazy_handlers(settings):
    return patterns


@plugin.url_lazy(lazy_handlers)
def torrent_info(bot, trigger):
    for name, provider in bot.memory['torrentinfo_providers'].items():
        if provider.link_pattern().match(trigger.group(0)):
            break

    display_name = provider.display_name()
    fetch_url = provider.get_fetch_url(trigger)

    try:
        r = requests.get(url=fetch_url, timeout=(10.0, 4.0))
    except requests.exceptions.ConnectTimeout:
        return bot.say("[{}] Connection timed out.".format(display_name))
    except requests.exceptions.ConnectionError:
        return bot.say("[{}] Couldn't connect to server.".format(display_name))
    except requests.exceptions.ReadTimeout:
        return bot.say("[{}] Server took too long to send data.".format(display_name))
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return bot.say("[{}] HTTP error: ".format(display_name) + str(e))

    bot.say("[{}] ".format(display_name) + ' | '.join([s.strip() for s in provider.parse(r)]))
