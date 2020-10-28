{
    'name': 'Birthday Wish & Reminder',

    'version': '14.0.0.1',

    'category': 'Human Resources',
    'summary': 'Employee Birthday Wish & Reminder',

    'description': """
        Send email Birthday Wish to Employee
        Send email Reminder To Manager for Birthday Wish
    """,

    'author': "Heliconia Solutions Pvt. Ltd.",
    'website': "https://heliconia.io/",

    'depends': ['hr'],

    'data': [
        'data/birthday_reminder_cron.xml',
        'data/mail_templates.xml',
        'data/ir_config_settings_data.xml',
        'views/res_config_settings_views.xml',
    ],

    'images': ['static/description/heliconia_birthday_reminder_wish.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
