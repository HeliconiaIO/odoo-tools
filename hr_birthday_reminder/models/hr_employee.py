# -*- coding: utf-8 -*-

from odoo import models, api, fields
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResUsers(models.Model):
    _inherit = "res.users"

    # @api.multi
    # def get_employees(self):
    #     today_date = datetime.today()
    #     results = self.env['hr.employee'].search([('birthday', '!=', False)])
    #     reminder_before_day = self.env['ir.config_parameter'].sudo().get_param("employee.reminder_before_day")
    #     employees = self.env['hr.employee']
    #     for employee in results:
    #         emp_day = (employee.birthday - timedelta(days=int(reminder_before_day))).day
    #         if today_date.day == emp_day and today_date.month == employee.birthday.month:
    #             employees += employee
    #     return employees

    @api.model
    def get_employee_birthday_info(self):
        reminder_before_day = self.env['ir.config_parameter'].sudo().get_param("employee.reminder_before_day")
        next_date = datetime.today() + timedelta(days=int(reminder_before_day or 1))
        employee_ids = self.env['hr.employee'].search([('birthday_date', '=', next_date.day),
                                                       ('birthday_month', '=', next_date.month)])
        return {'employees': employee_ids, 'date': next_date.strftime(DEFAULT_SERVER_DATE_FORMAT)}


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    birthday_date = fields.Integer(compute="_get_birthday_identifier", store=1)
    birthday_month = fields.Integer(compute="_get_birthday_identifier", store=1)

    @api.multi
    @api.depends('birthday')
    def _get_birthday_identifier(self):
        for employee in self.filtered(lambda e: e.birthday):
            employee.birthday_date = employee.birthday.day
            employee.birthday_month = employee.birthday.month

    @api.model
    def email_to_manager(self):
        user_group = self.env.ref("hr.group_hr_manager")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ", ".join(email_list)

    # @api.multi
    # def send_birthday_reminder_employee(self):
    #     today_date = datetime.today()
    #     IrConfigParameter = self.env['ir.config_parameter'].sudo()
    #     send_employee = IrConfigParameter.get_param("employee.send_wish_employee")
    #     send_manager = IrConfigParameter.get_param("employee.send_wish_manager")
    #     emp_template_id = IrConfigParameter.get_param("employee.emp_wish_template_id")
    #     manager_template_id = IrConfigParameter.get_param("employee.manager_wish_template_id")
    #     for employee in self.env['hr.employee'].search([]):
    #         if employee.birthday and send_employee == 'True':
    #             emp_day = employee.birthday.day
    #             if today_date.day == emp_day and today_date.month == employee.birthday.month and emp_template_id:
    #                 template_id = self.env['mail.template'].sudo().browse(int(emp_template_id))
    #                 template_id.send_mail(employee.id, force_send=True)
    #
    #     for manager_id in self.env.ref('hr.group_hr_manager').users:
    #         employees = self.env["res.users"].get_employees()
    #         if employees and send_manager == 'True':
    #             template_id = self.env['mail.template'].sudo().browse(int(manager_template_id))
    #             template_id.send_mail(manager_id.id, force_send=True)

    @api.model
    def send_birthday_reminder_employee(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        template_env = self.env['mail.template']
        send_employee = IrConfigParameter.get_param("employee.send_wish_employee")
        send_manager = IrConfigParameter.get_param("employee.send_wish_manager")
        # Send birthday wish to employee
        if send_employee == 'True':
            domain = [('birthday_date', '=', datetime.today().day), ('birthday_month', '=', datetime.today().month)]
            emp_template_id = IrConfigParameter.get_param("employee.emp_wish_template_id")
            template_id = template_env.sudo().browse(int(emp_template_id))
            for employee in self.env['hr.employee'].search(domain):
                template_id.send_mail(employee.id)

        # Send birthday reminder to HR manager
        if send_manager == 'True':
            birthday_info = self.env['res.users'].get_employee_birthday_info()
            if len(birthday_info.get('employees')):
                manager_template_id = IrConfigParameter.get_param("employee.manager_wish_template_id")
                template_id = template_env.sudo().browse(int(manager_template_id))
                for manager in self.env.ref('hr.group_hr_manager').users:
                    template_id.send_mail(manager.id)
