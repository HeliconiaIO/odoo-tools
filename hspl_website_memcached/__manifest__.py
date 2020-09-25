# -*- coding: utf-8 -*-
{
    'name': "Website Memcached",

    'summary': """
        HSPL Website Memcached""",

    'description': """
        HSPL Website Memcached
    """,

    'author': "Heliconia Solutions Pvt.Ltd.",
    'website': "https://heliconia.io",

    'category': 'website',
    'version': '12.0.0.1',

    'depends': ['base', 'website'],

    'data': [
        'data/ir_config_parameter.xml',
        'data/ir_corn.xml',
        'views/res_config_view.xml',
        'views/website_view.xml',
    ],

}
