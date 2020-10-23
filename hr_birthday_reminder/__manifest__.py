{
    'name': 'Employee Birthday Reminder',

    'version': '12.0.0.1',

    'category': 'hr',
    'summary': 'Birthday Reminder for Employee',

    'description': """
        This module send email notification to wish birthday
        * Employee
    """,

    'author': "Heliconia Solutions Pvt. Ltd.",
    'website': "https://heliconia.io/",

    'depends': ['base', 'hr'],

    'data': [
        'data/birthday_reminder_cron.xml',
        'data/mail_template_birthday_data.xml',
        'data/ir_configparameter_view.xml',
        'views/res_config_Setting_view.xml',
    ],

    'images': ['static/description/heliconia_employee_birthday_reminder.png'],

    'installable': True,
    'auto_install': False,
    'application': True,
}
