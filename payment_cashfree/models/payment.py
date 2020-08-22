# -*- coding: utf-8 -*-
# Copyright 2018, 2020 Heliconia Solutions Pvt Ltd (https://heliconia.io)

import hashlib
import hmac
import base64

from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare

import logging

_logger = logging.getLogger(__name__)


class PaymentAcquirerCashfree(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('cashfree', 'Cashfree')])
    cashfree_app_id = fields.Char(string='App id', required_if_provider='cashfree', groups='base.group_user')
    cashfree_secret_key = fields.Char(string='Secret Key', required_if_provider='cashfree', groups='base.group_user')

    def _get_cashfree_urls(self, environment):
        """ Cashfree URLs"""
        if environment == 'prod':
            return {'cashfree_form_url': 'https://www.cashfree.com/checkout/post/submit'}
        else:
            return {'cashfree_form_url': 'https://test.cashfree.com/billpay/checkout/post/submit'}

    def _cashfree_generate_sign(self, inout, postData):
        if inout not in ('in', 'out'):
            raise Exception("Type must be 'in' or 'out'")
        message = False
        if inout == 'out':
            sortedKeys = sorted(postData)
            signatureData = ""
            for key in sortedKeys:
                signatureData += key + str(postData[key]);
            message = signatureData.encode('utf-8')

        elif inout == 'in':
            signatureData = postData["orderId"] + postData["orderAmount"] + postData["referenceId"] + \
                            postData["txStatus"] + postData["paymentMode"] + postData["txMsg"] + postData["txTime"]
            message = signatureData.encode('utf-8')
        secret = self.cashfree_secret_key.encode('utf-8')
        signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
        return signature

    @api.multi
    def cashfree_form_generate_values(self, values):
        self.ensure_one()
        base_url = self.get_base_url()
        cashfree_values = dict(appId=self.cashfree_app_id,
                               orderId=values['reference'],
                               orderAmount=values['amount'],
                               orderCurrency=values['currency'].name,
                               customerName=values.get('partner_name'),
                               customerEmail=values.get('partner_email'),
                               customerPhone=values.get('partner_phone'),
                               returnUrl=urls.url_join(base_url, '/payment/cashfree/return'),
                               notifyUrl=urls.url_join(base_url, '/payment/cashfree/notify'),
                               )
        cashfree_values['signature'] = self._cashfree_generate_sign('out', cashfree_values)
        values.update(cashfree_values)
        return values

    @api.multi
    def cashfree_get_form_action_url(self):
        self.ensure_one()
        return self._get_cashfree_urls(self.environment)['cashfree_form_url']


class PaymentTransactionCashfree(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _cashfree_form_get_tx_from_data(self, data):

        postData = {
            "orderId": data.get('orderId'),
            "orderAmount": data.get('orderAmount'),
            "referenceId": data.get('referenceId'),
            "txStatus": data.get('txStatus'),
            "paymentMode": data.get('paymentMode'),
            "txMsg": data.get('txMsg'),
            "txTime": data.get('txTime'),
        }

        reference = postData.get('orderId')
        signature = data.get('signature')

        transaction = self.search([('reference', '=', reference)])

        if not transaction:
            error_msg = (_('Cashfree: received data for reference %s; no order found') % (reference))
            raise ValidationError(error_msg)
        elif len(transaction) > 1:
            error_msg = (_('Cashfree: received data for reference %s; multiple orders found') % (reference))
            raise ValidationError(error_msg)

        if not postData.get('referenceId'):
            raise ValidationError(_('Cashfree: received data with missing reference (%s)') % (reference))

        shasign_check = transaction.acquirer_id._cashfree_generate_sign('in', data)
        shasign_check = shasign_check and shasign_check.decode("utf-8")
        if shasign_check.upper() != signature.upper():
            raise ValidationError(_('Cashfree: invalid shasign, received %s, computed %s, for data %s') % (
                                     signature, shasign_check, data))

        return transaction

    @api.multi
    def _cashfree_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        if self.acquirer_reference and data.get('referenceId') != self.acquirer_reference:
            invalid_parameters.append(
                ('Transaction Id', data.get('referenceId'), self.acquirer_reference))
        if float_compare(float(data.get('orderAmount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(
                ('Amount', data.get('amount'), '%.2f' % self.amount))
        return invalid_parameters

    @api.multi
    def _cashfree_form_validate(self, data):
        status = data.get('txStatus')
        result = self.write({
            'acquirer_reference': data.get('referenceId'),
            'date': fields.Datetime.now(),
        })
        if status == 'SUCCESS':
            self._set_transaction_done()
        elif status in ['FAILED', 'CANCELLED', 'FLAGGED']:
            self._set_transaction_cancel()
        else:
            self._set_transaction_pending()
        return result
