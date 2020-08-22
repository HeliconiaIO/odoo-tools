# -*- coding: utf-8 -*-
# Copyright 2018, 2020 Heliconia Solutions Pvt Ltd (https://heliconia.io)

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CashfreeController(http.Controller):

    @http.route(['/payment/cashfree/return', '/payment/cashfree/cancel', '/payment/cashfree/error',
                 '/payment/cashfree/notify'], type='http', auth='public', csrf=False)
    def cashfree_return(self, **post):
        """ Cashfree."""
        _logger.info(
            'Cashfree: entering form_feedback with post data %s', pprint.pformat(post))
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'cashfree')
        return werkzeug.utils.redirect('/payment/process')
