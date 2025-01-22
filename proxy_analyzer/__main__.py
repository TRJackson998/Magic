"""
Proxied Card Processor
==================================
In Magic, players can "proxy" cards. This is when they print out a copy of a card they would 
like to play with but do not currently own.
Cards can be purchased as singles or in packs. Packs contain random cards from a specific set.
This program fills a MySQL table with cards that have been proxied 
and generates a list of card sets that should be 
purchased in order to maximize pulling cards that have been proxied.

Developer
---------
Terrence Jackson

Resources
---------
archidekt.com
https://scryfall.com/docs/api/bulk-data
"""
