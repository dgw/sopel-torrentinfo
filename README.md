# sopel-torrentinfo

Sopel plugin to fetch info for torrent links.

## Current status

The current support is very limited, just a proof of doing something. It
fetches only from Nyaa.si, and then only a very few details. More information
(and possibly other supported sites) will come later.

## Requirements

The `torrentinfo` plugin relies on Sopel 7.1+ and the following PyPI packages:

* `cssselect`
* `etree` from `lxml`
* `requests`

Only tested on Python 3, due to Python 2 reaching EOL on January 1, 2020.

## Usage

There are no commands. Just enable the plugin and it will fetch info about
supported torrents automatically when links appear in chat.
