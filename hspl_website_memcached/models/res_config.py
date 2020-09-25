# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    memcached_db = fields.Char(string='Memcached Databases', default='("localhost", 11211)',
                               help="A list of memcached databases ('server',<port>)")
    memcached_expiry_sec = fields.Char(string='Memcached Expiry Second', default=86400,
                                       help="Memcached Key Expiry Seconds")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            memcached_db=self.env['ir.config_parameter'].get_param(
                'website_memcached.memcached_db') or '("localhost", 11211)',
            memcached_expiry_sec=self.env['ir.config_parameter'].get_param(
                'memcached.expiry.seconds') or 86400,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('website_memcached.memcached_db', self.memcached_db)
        self.env['ir.config_parameter'].set_param('memcached.expiry.seconds', self.memcached_expiry_sec)
