# coding=utf-8
"""
torrentinfo - Sopel plugin to fetch info for torrent links
"""

import pkg_resources

import requests

from sopel import plugin

from .providers import ProviderManager


provider_manager = ProviderManager()


def setup(bot):
    entry_points = pkg_resources.iter_entry_points('sopel_torrentinfo.providers')

    for entry_point in entry_points:
        provider = entry_point.load()
        provider_manager.register_provider(provider)


def lazy_handlers(settings):
    return provider_manager.providers.keys()


@plugin.url_lazy(lazy_handlers)
def torrent_info(bot, trigger):
    provider = provider_manager.map_url_to_provider(trigger.group(0))

    if provider is None:
        raise RuntimeError("It shouldn't be possible to get here.")

    display_name = provider.DISPLAY_NAME
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
