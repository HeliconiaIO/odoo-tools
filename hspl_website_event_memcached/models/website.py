# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.hspl_website_memcached.models import memcached


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.one
    def do_draft(self):
        super(EventRegistration, self).do_draft()
        for key in memcached.get_keys(flush_type='event register %s' % self.event_id.name):
            memcached.mc_delete(key)

    @api.one
    def confirm_registration(self):
        super(EventRegistration, self).confirm_registration()
        for key in memcached.get_keys(flush_type='event register %s' % self.event_id.name):
            memcached.mc_delete(key)

    @api.one
    def button_reg_close(self):
        for key in memcached.get_keys(flush_type='event register %s' % self.event_id.name):
            memcached.mc_delete(key)
        super(EventRegistration, self).button_reg_close()

    @api.one
    def button_reg_cancel(self):
        super(EventRegistration, self).button_reg_cancel()
        for key in memcached.get_keys(flush_type='event register %s' % self.event_id.name):
            memcached.mc_delete(key)


class Website(models.Model):
    _inherit = 'website'

    def get_kw_event(self, kw):
        return kw['event'].name if kw.get('event', None) else ''
