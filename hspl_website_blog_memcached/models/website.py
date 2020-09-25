# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Website(models.Model):
    _inherit = 'website'

    def get_kw_blog(self, kw):
        return kw['blog'].name if kw.get('blog', None) else ''
