# -*- coding: utf-8 -*-

{
    'name': 'Website MemCached Event',

    'summary': 'website acceleration for event using memcached',

    'description': """
        Add mechanisms to cache rendered event pages
        This module depends on website_memcached
    """,

    'author': "Heliconia Solutions PVT LTD",
    'website': "https://heliconia.io/",

    'version': '1.0',
    'category': 'website',

    'depends': ['hspl_website_memcached', 'website_event'],

    'external_dependencies': {'python': ['pymemcache', ]},

    'data': [],
}
