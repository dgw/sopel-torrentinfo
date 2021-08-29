# coding=utf-8
"""Link handling provider logic."""


import abc
import re

from lxml import etree


class TorrentInfoProvider(abc.ABC):
    """Base class for torrent link info providers."""

    @staticmethod
    @abc.abstractmethod
    def link_pattern():
        """Must return a compiled regex pattern matching links this provider can handle."""

    @classmethod
    def display_name(cls):
        """Define a human-readable name for this provider.

        For example, ``Nyaa`` or ``TokyoTosho``.

        If not overridden, will return the class's ``__name__``.
        """
        return cls.__name__

    @staticmethod
    @abc.abstractmethod
    def get_fetch_url(trigger):
        """Return the URL to fetch, given a matching URL ``trigger``."""

    @staticmethod
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

    @staticmethod
    def link_pattern():
        return re.compile(r'https?:\/\/(?:www\.)?nyaa\.si\/(?:view|download)\/(\d+)')

    @staticmethod
    def get_fetch_url(trigger):
        return 'https://nyaa.si/view/%s' % trigger.group(1)

    @staticmethod
    def parse(response):
        page = etree.HTML(response.content)

        t = []

        t.append(page.cssselect('meta[property="og:title"]')[0].get('content').replace(' :: Nyaa', ''))
        t.append(page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 1)[0])
        t.append(page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 2)[1])
        t.append(page.cssselect('meta[property="og:description"]')[0].get('content').split("|", 3)[2])
        t.append(response.url)

        return t
