# -*- coding: utf-8 -*-

from odoo.addons.hspl_website_memcached.models import memcached
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInherit(WebsiteSale):

    # '/shop
    @memcached.route()
    def shop(self, page=0, category=None, search='', **post):
        return super(WebsiteSaleInherit, self).shop(page, category, search, **post)

    # '/shop/product/<model("product.template"):product>'
    @memcached.route()
    def product(self, product, category='', search='', **kwargs):
        return super(WebsiteSaleInherit, self).product(product, category, search, **kwargs)

    # '/shop/pricelist'
    @memcached.route()
    def pricelist(self, promo, **post):
        return super(WebsiteSaleInherit, self).pricelist(promo, **post)

    # '/shop/cart'
    @memcached.route()
    def cart(self, **post):
        return super(WebsiteSaleInherit, self).cart(**post)

    # '/shop/cart/update'
    @memcached.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **post):
        return super(WebsiteSaleInherit, self).cart_update(product_id, add_qty, set_qty, **post)

    # '/shop/checkout'
    @memcached.route()
    def checkout(self, **post):
        return super(WebsiteSaleInherit, self).checkout(**post)

    # '/shop/confirm_order'
    @memcached.route()
    def confirm_order(self, **post):
        return super(WebsiteSaleInherit, self).confirm_order(**post)

    # '/shop/payment'
    @memcached.route()
    def payment(self, **post):
        return super(WebsiteSaleInherit, self).payment(**post)

    # '/shop/payment/validate'
    @memcached.route()
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        return super(WebsiteSaleInherit, self).payment_validate(transaction_id, sale_order_id, **post)

    # '/shop/confirmation'
    @memcached.route()
    def payment_confirmation(self, **post):
        return super(WebsiteSaleInherit, self).payment_confirmation(**post)
