# -*- coding: utf-8 -*-
# © 2020 Heliconia Solutions Pvt. Ltd., < hello@heliconia.io >

{
    'name': 'Theme Emerald',
    'description': 'A Responsive Bootstrap Theme for Odoo CMS',
    'category': 'Theme/Business',
    'summary': '',
    'version': '14.0.0.1.0',
    'license': 'OPL-1',
    'depends': ['base','website', 'website_crm'],
    'data': [
        'templates/assets.xml',
        'templates/headers.xml',
        'templates/footer.xml',
        'templates/customize_options.xml',
        'templates/snippets.xml',
        'templates/contact.xml',
    ],
    'images': [
        'static/description/screenshot.png',
    ],

    'author': "Heliconia Solutions Pvt. Ltd.",

    'application': False,
    'installable': True,
    'auto_install': False,

}
