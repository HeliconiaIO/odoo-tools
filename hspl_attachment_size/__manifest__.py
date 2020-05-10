# -*- coding: utf-8 -*-
# Copyright 2018, 2020 Heliconia Solutions Pvt Ltd (https://heliconia.io)
{
    'name': "Attachment Size",

    'summary': """
        Compute Attachment size in ir.attachment For Odoo V13 Community and Enterprise """,

    'description': """
        Compute Attachment size in ir.attachment
    """,

    'author': "Heliconia Solutions Pvt ltd",
    'website': "http://heliconia.in/",

    'category': 'base',
    'version': '13.0.1',
    "license": "OPL-3",

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
