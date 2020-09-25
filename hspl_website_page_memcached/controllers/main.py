# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.hspl_website_memcached.models import memcached
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.main import Binary


class CachedWebsite(Website):

    @memcached.route(flush_type=lambda kw: 'page_meta')
    def robots(self):
        return super(CachedWebsite, self).robots()

    @memcached.route(flush_type=lambda kw: 'page_meta')
    def sitemap_xml_index(self):
        return super(CachedWebsite, self).sitemap_xml_index()

    @memcached.route(flush_type=lambda kw: 'page_meta')
    def website_info(self):
        return super(CachedWebsite, self).website_info()


class CachedBinary(Binary):

    @memcached.route(flush_type=lambda kw: 'page_image', binary=True)
    def company_logo(self, dbname=None, **kw):
        return super(CachedBinary, self).company_logo(dbname, **kw)
