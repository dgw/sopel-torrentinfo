# sopel-torrentinfo
Sopel module that fetches info about torrent links

## Current status

The current support is very limited, just a proof of doing something. It fetches
only from Nyaa.si and Anidex.info, and then only a very few details. More information (and possibly
other supported sites) will come later.

## Requirements
The torrentinfo module relies on the following Python components:

* `etree` from `lxml`
* `requests`

## Usage
There are no commands. Just enable the module and it will fetch info about
supported torrents automatically.

## Known issues
If the uploader on Nyaa.si is Anonymous, it will just show empty space.