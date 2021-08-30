# coding=utf-8
"""Link handling provider logic."""


import abc
import re

from lxml import etree


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
        t.append(response.url)

        return t
