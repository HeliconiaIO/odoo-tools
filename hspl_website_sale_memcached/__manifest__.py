# -*- coding: utf-8 -*-
{
    'name': 'Website MemCached Sale',

    'summary': 'website acceleration for sale using memcached',

    'description': """
        Add mechanisms to cache rendered sale pages
        This module depends on website_memcached
    """,

    'author': "Heliconia Solutions PVT LTD",
    'website': "https://heliconia.io/",

    'version': '1.0',
    'category': 'website',

    'depends': ['hspl_website_memcached', 'website_sale'],

    'external_dependencies': {'python': ['pymemcache', ]},

    'data': [],
}
