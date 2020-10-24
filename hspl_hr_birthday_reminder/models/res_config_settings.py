# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    send_wish_employee = fields.Boolean(string='Send birthday with to employee?')
    emp_wish_template_id = fields.Many2one('mail.template', string='Employee Email Template',
                                           domain=[('model', '=', 'hr.employee')])
    send_wish_manager = fields.Boolean(string='Send employee birthday reminder to HR Manager')
    manager_wish_template_id = fields.Many2one('mail.template', string='Manager Email Template',
                                               domain=[('model', '=', 'res.users')])
    reminder_before_day = fields.Integer(string='Send reminder before days')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        send_wish_employee = IrConfigParameter.get_param("employee.send_wish_employee")
        emp_wish_template_id = IrConfigParameter.get_param("employee.emp_wish_template_id")
        send_wish_manager = IrConfigParameter.get_param("employee.send_wish_manager")
        manager_wish_template_id = IrConfigParameter.get_param("employee.manager_wish_template_id")
        reminder_before_day = IrConfigParameter.get_param("employee.reminder_before_day")
        res.update(
            send_wish_employee=True if send_wish_employee == 'True' else False,
            emp_wish_template_id=int(emp_wish_template_id),
            send_wish_manager=True if send_wish_manager == 'True' else False,
            manager_wish_template_id=int(manager_wish_template_id),
            reminder_before_day=int(reminder_before_day),
        )
        return res

    def set_values(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        super(ResConfigSettings, self).set_values()
        IrConfigParameter.set_param("employee.send_wish_employee", 'True' if self.send_wish_employee else 'False')
        IrConfigParameter.set_param("employee.emp_wish_template_id", self.emp_wish_template_id.id or False)
        IrConfigParameter.set_param("employee.send_wish_manager", 'True' if self.send_wish_manager else 'False')
        IrConfigParameter.set_param("employee.manager_wish_template_id", self.manager_wish_template_id.id or False)
        IrConfigParameter.set_param("employee.reminder_before_day", self.reminder_before_day or 0)
