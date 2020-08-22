# -*- coding: utf-8 -*-
# Copyright 2018, 2020 Heliconia Solutions Pvt Ltd (https://heliconia.io)

{
    'name': "Payment Cashfree",
    'summary': """Payment Acquirer: Cashfree Implementation""",
    'description': """Payment Acquirer: Cashfree Implementation""",
    'category': 'Payment Acquirer',

    'author': 'Heliconia Solutions Pvt. Ltd.',
    'company': 'Heliconia Solutions Pvt. Ltd.',
    'website': 'https://heliconia.io',

    'version': '12.0.1.0.0',
    'license': 'OPL-1',
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_cashfree_templates.xml',
        'data/payment_acquirer_data.xml',
    ],

    'images': ['static/description/heliconia_odoo_cashfree.gif'],

    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',

}
