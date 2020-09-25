# -*- coding: utf-8 -*-

from odoo.http import request
from odoo.addons.hspl_website_memcached.models import memcached
from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEvent(WebsiteEventController):

    @memcached.route()
    def events(self, page=1, **searches):
        return super(WebsiteEvent, self).events(page, **searches)

    # '/event/<model("event.event"):event>/page/<path:page>'
    @memcached.route(flush_type=lambda kw: 'event %s' % request.website.get_kw_event(kw))
    def event_page(self, event, page, **post):
        return super(WebsiteEvent, self).event_page(event, page, **post)

    # '/event/<model("event.event"):event>/register'
    @memcached.route(flush_type=lambda kw: 'event register %s' % request.website.get_kw_event(kw))
    def event_register(self, event, **post):
        return super(WebsiteEvent, self).event_register(event, **post)

    # '/event/get_country_event_list'
    @memcached.route()
    def get_country_events(self, **post):
        return super(WebsiteEvent, self).get_country_events(**post)
