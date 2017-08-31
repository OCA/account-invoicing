# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# © 2017 Odoo SA <https://www.odoo.com>
# © 2017 OCA <https://odoo-community.org>
# License LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.en.html).
import json
from openerp.tests import common
from openerp import fields


class TestAccountOutstandingPayments(common.TransactionCase):

    post_install = True

    def test_account_outstanding_payments(self):
        res_partner_model = self.env['res.partner']
        sale_order_model = self.env['sale.order']
        product_product_model = self.env['product.product']
        journal_cash = self.env['account.journal'].search(
            [('code', '=', 'BNK1')])
        res_partner = res_partner_model.create(
            {'name': 'James'})
        period_id = self.env['account.period'].search(
            [('code', '=', '00/2017')])
        account_id = self.env['account.account'].search(
            [('code', '=', 200000)])
        product = product_product_model.create({'name': 'Product 1'})
        # create a sale.order with one line
        sale_order = sale_order_model.create(
            {'partner_id': res_partner.id,
             'date_order': fields.Datetime.now()})
        self.env['sale.order.line'].create({
            'name': product.name,
            'product_id': product.id,
            'product_uom_qty': 1,
            'order_id': sale_order.id,
            'price_unit': 100})
        sale_order.action_button_confirm()
        # create the invoice for that sale.order
        self.env['sale.advance.payment.inv'].with_context(
            {'active_ids': sale_order.ids}).create(
                {'advance_payment_method': 'all',
                 'amount': 50,
                 'qtty': 1}).create_invoices()
        # validate invoice
        account_invoice = sale_order.invoice_ids[0]
        account_invoice.signal_workflow('invoice_open')
        # make a payment on that invoice, keep it open
        proforma_voucher = self.env['account.voucher'].with_context(
            account_invoice.invoice_pay_customer()['context']) \
            .create({'partner_id': res_partner.id,
                     'amount': 50,
                     'journal_id': journal_cash.id,
                     'period_id': period_id.id,
                     'account_id': account_id.id,
                     'payment_option': 'without_writeoff'})
        proforma_voucher.button_proforma_voucher()
        # check if the widget shows the remaining money to be paid
        self.assertEqual(json.loads(
            account_invoice.outstanding_credits_debits_widget)[
                'content'][0]['amount'], 50.0, 'Incorrect payment info')
