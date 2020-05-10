# -*- coding: utf-8 -*-
# Copyright 2018, 2020 Heliconia Solutions Pvt Ltd (https://heliconia.io)
{
    'name': "Attachment Size",

    'summary': """
        Attachment size in tree & form view """,

    'description': """
        Attachment size in tree & form view
    """,

    'author': "Heliconia Solutions Pvt. Ltd.",
    'website': "http://heliconia.io/",

    'category': 'Tools',
    'version': '13.0.1',

    'depends': ['base'],

    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',

    'images': ['static/description/heliconia_attachment_size.gif'],

}
