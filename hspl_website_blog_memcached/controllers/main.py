# -*- coding: utf-8 -*-

from odoo.http import request
from odoo.addons.hspl_website_memcached.models import memcached
from odoo.addons.website_blog.controllers.main import WebsiteBlog


class CachedBlog(WebsiteBlog):

    @memcached.route(flush_type=lambda kw: 'blog %s' % request.website.get_kw_blog(kw))
    def blog(self, blog=None, tag=None, page=1, **opt):
        return super(CachedBlog, self).blog(blog, tag, page, **opt)

    @memcached.route(flush_type=lambda kw: 'blog %s' % request.website.get_kw_blog(kw))
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        return super(CachedBlog, self).blog_post(blog, blog_post, tag_id, page, enable_editor, **post)
