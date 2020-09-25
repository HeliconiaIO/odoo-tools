# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.hspl_website_memcached.models import memcached
import werkzeug


class MemCachedController(http.Controller):

    @http.route(['/mcpage/<string:key>', ], type='http', auth="user", website=True)
    def memcached_page(self, key='', **post):
        page_dict = memcached.mc_load(key)
        if page_dict:
            return page_dict.get('page').decode('base64')
        return request.env['ir.http']._handle_exception(404)

    @http.route(['/mcpage/<string:key>/delete', ], type='http', auth="user", website=True)
    def memcached_page_delete(self, key='', **post):
        memcached.mc_delete(key)
        if post.get('url'):
            return werkzeug.utils.redirect(post.get('url'), 302)
        return http.Response('<h1>Key is deleted %s</h1>' % (key))

    @http.route(['/mcmeta/<string:key>', ], type='http', auth="user", website=True)
    def memcached_meta(self, key='', **post):
        res = memcached.mc_meta(key)
        values = {
            'url': '/mcpage/%s' % key,
            'key': key,
            'page_dict': res['page_dict'].items(),
            'page_len': '%.2f' % res['size'],
        }
        return request.render('hspl_website_memcached.mcmeta_page', values)

    @http.route(['/mcflush', '/mcflush/<string:flush_type>', ], type='http', auth="user", website=True)
    def memcached_flush(self, flush_type='all', **post):
        return memcached.get_flush_page(memcached.get_keys(flush_type=flush_type, load=True),
                                        'Cached Pages %s' % flush_type, '/mcflush/%s' % flush_type,
                                        '/mcflush/%s/delete' % flush_type)

    @http.route(['/mcetag', '/mcetag/<string:etag>', ], type='http', auth="user", website=True)
    def memcached_etag(self, etag='all', **post):
        return memcached.get_flush_page(memcached.get_keys(etag=etag, load=True), 'Cached Pages Etag %s' % etag,
                                        '/mcetag/%s' % etag, '/mcetag/%s/delete' % etag)

    @http.route(['/mcflush/<string:flush_type>/delete', ], type='http', auth="user", website=True)
    def memcached_flush_delete(self, flush_type='all', **post):
        memcached.mc_delete(memcached.get_keys(flush_type=flush_type))
        return werkzeug.utils.redirect('/mcflush/%s' % flush_type, 302)

    @http.route(['/mcmodule', '/mcmodule/<string:module>', ], type='http', auth="user", website=True)
    def memcached_module(self, module='all', **post):
        return memcached.get_flush_page(memcached.get_keys(module=module, load=True), 'Cached Pages Model %s' % module,
                                        '/mcmodule/%s' % module, '/mcmodule/%s/delete' % module)

    @http.route(['/mcmodule/<string:module>/delete', ], type='http', auth="user", website=True)
    def memcached_module_delete(self, module='all', **post):
        memcached.mc_delete(memcached.get_keys(module=module))
        return werkzeug.utils.redirect('/mcmodule/%s' % module, 302)

    @http.route(['/mcpath', ], type='http', auth="user", website=True)
    def memcached_path(self, path='all', **post):
        return memcached.get_flush_page(memcached.get_keys(path=path, load=True), 'Cached Pages Path %s' % path,
                                        '/mcpath?path=%s' % path, '/mcpath/delete?path=%s' % path)

    @http.route(['/mcpath/delete', ], type='http', auth="user", website=True)
    # Example: /mcpath/delete?path=/foo/bar
    def memcached_path_delete(self, path='all', **post):
        if memcached.get_keys(path=path):
            memcached.mc_delete(memcached.get_keys(path=path))
        return werkzeug.utils.redirect('/mcpath?path=%s' % path, 302)

    @http.route(['/mcstatus', '/mcstatus/<int:status_code>', ], type='http', auth="user", website=True)
    def memcached_status_code(self, status_code='all', **post):
        return memcached.get_flush_page(memcached.get_keys(status_code=status_code, load=True),
                                        'Cached Pages Status %s' % status_code, '/mcstatus/%s' % status_code,
                                        '/mcstatus/%s/delete' % status_code)

    @http.route(['/mcstatus/all/delete', '/mcstatus/<int:status_code>/delete', ], type='http', auth="user",
                website=True)
    def memcached_status_code_delete(self, status_code='all', **post):
        memcached.mc_delete(memcached.get_keys(status_code=status_code))
        return werkzeug.utils.redirect('/mcstatus/%s' % status_code, 302)

    @http.route(['/mcclearpath', ], type='http', auth="user", website=True)
    def memcached_clear_path(self, path='all', **post):
        memcached.mc_delete(memcached.get_keys(path=path))
        return request.redirect(path, code=302)

    @http.route(['/mcstats', ], type='http', auth="user", website=True)
    def memcached_stats(self, **post):
        x = memcached.MEMCACHED_CLIENT().stats('items')
        items = {y.decode('utf-8'): x.get(y) for y in x.keys()}
        x = memcached.MEMCACHED_CLIENT().stats()
        stats = {y.decode('utf-8'): x.get(y) for y in x.keys()}
        slab_limit = {k.split(':')[1]: v for k, v in items.items() if
                      k.split(':')[2] == 'number'}
        key_lists = [memcached.MEMCACHED_CLIENT().stats('cachedump', slab, str(limit)) for slab, limit in
                     slab_limit.items()]
        values = {'items': items.items(),
                  'slab_limit': slab_limit.items(),
                  'stats': stats.items(),
                  'keys': [key for sublist in key_lists for key in sublist.keys()]}
        return request.render('hspl_website_memcached.statistics_page', values)

    @http.route(['/memcache/stats', ], type='http', auth="user", website=True)
    def memcache_statistics(self, **post):
        x = request.website.memcache_get_stats('slabs')
        slab_stats = {y.decode('utf-8'): x.get(y) for y in x.keys()}
        slabs = {}
        delete_key = []
        for key in slab_stats.keys():
            key_s = key.split(':')
            if len(key_s) > 1:
                value = slab_stats[key]
                key_name = key_s[1]
                slab = int(key_s[0])
                if slab not in slabs:
                    slabs[slab] = {}
                slabs[slab][key_name] = value
                delete_key.append(key)
        if delete_key:
            for key in delete_key:
                del slab_stats[key]
        slab_stats['slabs'] = slabs
        x = request.website.memcache_get_stats()
        memcache_get_stats = {y.decode('utf-8'): x.get(y) for y in x.keys()}
        x = request.website.memcache_get_stats('items')
        memcach_items = {y.decode('utf-8'): x.get(y) for y in x.keys()}
        stats_desc = request.website.memcache_get_stats_desc()
        get_stats_desc = request.website.memcache_get_stats_desc('slabs')
        items_desc = request.website.memcache_get_stats_desc('items')
        values = {
            'stats': memcache_get_stats,
            'slabs': slab_stats,
            'items': memcach_items,
            'stats_desc': stats_desc,
            'slabs_desc': get_stats_desc,
            'items_desc': items_desc,
            # 'sizes': request.website.memcache_get_stats('sizes'), # disabled?
            # 'detail': request.website.memcache_get_stats('detail', 'dump'), # not sure how to use it. on|off|dump = error|error|empty
            'sorted': sorted,
        }
        return request.render('hspl_website_memcached.statistics_page', values)
