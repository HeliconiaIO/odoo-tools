# -*- coding: utf-8 -*-
{
    'name': 'Website MemCached Blog',

    'summary': 'website acceleration for blog using memcached',

    'description': """
        Add mechanisms to cache rendered blog pages
        This module depends on hspl_website_memcached
    """,

    'author': "Heliconia Solutions PVT LTD",
    'website': "https://heliconia.io/",

    'version': '1.0',
    'category': 'website',

    'depends': ['hspl_website_memcached', 'website_blog'],

    'external_dependencies': {
        'python': ['pymemcache']
    },
}
