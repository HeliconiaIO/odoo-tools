# -*- coding: utf-8 -*-

from odoo import models, api, _
from datetime import datetime, timedelta


class ResUsers(models.Model):
    _inherit = "res.users"

    def get_employees(self):
        today_date = datetime.today()
        results = self.env['hr.employee'].search([('birthday', '!=', False)])
        reminder_before_day = self.env['ir.config_parameter'].sudo().get_param("employee.reminder_before_day")
        employees = self.env['hr.employee']
        for employee in results:
            emp_day = (employee.birthday - timedelta(days=int(reminder_before_day))).day
            if today_date.day == emp_day and today_date.month == employee.birthday.month:
                employees += employee
        return employees


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def email_to_manager(self):
        user_group = self.env.ref("hr.group_hr_manager")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ", ".join(email_list)

    def send_birthday_reminder_employee(self):
        today_date = datetime.today()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        send_employee = IrConfigParameter.get_param("employee.send_wish_employee")
        send_manager = IrConfigParameter.get_param("employee.send_wish_manager")
        emp_template_id = IrConfigParameter.get_param("employee.emp_wish_template_id")
        manager_template_id = IrConfigParameter.get_param("employee.manager_wish_template_id")
        for employee in self.env['hr.employee'].search([]):
            if employee.birthday and send_employee == 'True':
                emp_day = employee.birthday.day
                if today_date.day == emp_day and today_date.month == employee.birthday.month and emp_template_id:
                    template_id = self.env['mail.template'].sudo().browse(int(emp_template_id))
                    template_id.send_mail(employee.id, force_send=True)

        for manager_id in self.env.ref('hr.group_hr_manager').users:
            employees = self.env["res.users"].get_employees()
            if employees and send_manager == 'True':
                template_id = self.env['mail.template'].sudo().browse(int(manager_template_id))
                template_id.send_mail(manager_id.id, force_send=True)

