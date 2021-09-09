# sopel-torrentinfo

Sopel plugin to fetch info for torrent links.

## Site support

Sites supported at present:

* Nyaa
* TokyoTosho

Both are implemented with HTML scraping (see requirements below), as none of
the sites in this category ever seem to have APIs available.

### Add-ons

Other packages may add support for other sites' links by defining one or more
`setuptools` entry points under `sopel_torrentinfo.providers`, using this
plugin's `providers.TorrentInfoProvider` class as a base. The code itself is
the best documentation, for now; comments and built-in examples describe how
the interface works.

## Requirements

The `torrentinfo` plugin relies on Sopel 7.1+ and the following PyPI packages:

* `lxml` (for its `etree` module)
* `cssselect` (extends `lxml` with CSS-selector-based traversal)
* `requests` (Sopel itself requires this)

Requiring `lxml` and `cssselect` for this plugin's built-in site handlers
simply means that any add-on handlers are guaranteed to have those available.

Only tested on Python 3, due to Python 2 reaching EOL on January 1, 2020.

## Usage

There are no commands. Just enable the plugin and it will fetch info about
supported torrents automatically when links appear in chat.
