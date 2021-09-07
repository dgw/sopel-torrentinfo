# coding=utf-8
"""Link handling provider logic."""


import abc
from collections import OrderedDict
import re

from lxml import etree


class ProviderManager:
    """Manager of info providers. Possibly also slayer of dragons."""

    def __init__(self):
        self.providers = OrderedDict()
        """Mapping of each known provider's URL pattern to an instance of that provider."""
        # TODO: Can be a regular dict in py3.7+ only;
        # dict remembering insertion order is guaranteed as of py3.7

    def register_provider(self, provider):
        """Make the manager aware of ``provider`` and its URL pattern."""
        if not isinstance(provider, TorrentInfoProvider):
            try:
                provider = provider()
            except Exception:
                # doesn't matter what happened; bail if something's fucky
                raise ValueError("Not a TorrentInfoProvider subclass: %s" % provider)

        self.providers[provider.get_url_pattern()] = provider

    def remove_provider(self, provider):
        """Forget about ``provider`` and its URL pattern."""
        try:
            del self.providers[provider.get_url_pattern()]
        except KeyError:
            raise RuntimeError('Attempt to remove a provider that was not registered.')

    def map_url_to_provider(self, url):
        """Given ``url``, return an instance of the best-matching provider."""
        for pattern, provider in self.providers.items():
            if pattern.match(url):
                return provider

        # no matching provider
        # explicit better than implicit
        return None


class TorrentInfoProvider(abc.ABC):
    """Base class for torrent link info providers."""

    @property
    @abc.abstractmethod
    def URL_PATTERN(self):
        """Required URL pattern, as it would be passed to ``@plugin.url`` decorator."""

    def get_url_pattern(self):
        """Compile and return the URL pattern for Sopel's rule manager."""
        return re.compile(self.URL_PATTERN)

    @property
    def DISPLAY_NAME(self):
        """Define a human-readable name for this provider.

        For example, ``Nyaa`` or ``TokyoTosho``.

        If not overridden, will return the class's ``__name__``.
        """
        return self.__class__.__name__

    @abc.abstractmethod
    def get_fetch_url(self, trigger):
        """Return the URL to fetch, given a matching URL ``trigger``."""

    @abc.abstractmethod
    def parse(response):
        """Parse the fetched ``response`` data.

        The ``response`` is a ``requests.Response`` object, just as if the
        provider called ``requests.get()`` itself.

        This method is expected to return an iterable of pieces, for example::

            [
                'Title: 60th Annual Kohaku',
                'Uploader: NHK Official',
                'Size: 420.69 GiB',
                ...,
            ]

        These pieces will be joined together by the plugin's output stage, in
        combination with a prefix based on the provider's ``display_name()``.
        """


class Nyaa(TorrentInfoProvider):
    """Handler for Nyaa.si links."""

    URL_PATTERN = r'https?:\/\/(?:www\.)?nyaa\.si\/(?:view|download)\/(\d+)'

    def get_fetch_url(self, trigger):
        return 'https://nyaa.si/view/%s' % trigger.group(1)

    def parse(self, response):
        page = etree.HTML(response.content)

        t = []

        t.append(page.cssselect('meta[property="og:title"]')[0].get('content').replace(' :: Nyaa', ''))
        t.append(page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 1)[0])
        t.append(page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 2)[1])
        t.append(page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 3)[2])

        return t


class TokyoTosho(TorrentInfoProvider):
    """Handler for TokyoTosho links."""

    URL_PATTERN = r'https?:\/\/(?:www\.)?tokyotosho\.info\/details\.php\?id=(\d+)'

    def get_fetch_url(self, trigger):
        return 'https://www.tokyotosho.info/details.php?id=%s' % trigger.group(1)

    def parse(self, response):
        details = etree.HTML(response.content).cssselect('div.details')[0]
        items = []

        # title
        items.append(details.xpath('//a[@type="application/x-bittorrent"]/text()[normalize-space()]')[0])
        # category
        items.append(details.xpath('//li[contains(text(), "Torrent Type")]/following::li[1]/a/text()')[0])
        # size
        items.append(details.xpath('//li[contains(text(), "Filesize")]/following::li[1]/text()')[0])
        # submitter and timestamp
        items.append("Submitted by {} at {}".format(
            # user
            details.xpath('//li/em[contains(text(), "Submitter")]/following::li[1]/text()')[0].rstrip(),
            # timestamp
            details.xpath('//li[contains(text(), "Date Submitted")]/following::li[1]/text()')[0]
        ))

        return items
