# -*- coding: utf-8 -*-
{
    'name': "Image Importer",

    'summary': """
        Import Image file in to the appropriate record""",

    'description': """
        Module helps to add image from the csv or xls file.
    """,

    'author': 'Heliconia Solutions Pvt. Ltd.',

    'category': 'Tools',

    'website': 'https://heliconia.io',

    'version': '14.0.0.1',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/image_importer_wizard_views.xml',
    ],
}
