# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestAccountInvoiceSplit(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceSplit, self).setUp()
        self.AccountObj = self.env['account.account']
        self.InvoiceObj = self.env['account.invoice']
        self.InvoiceLineObj = self.env['account.invoice.line']
        self.SplitObj = self.env['account.invoice.split']

        self.account_type = self.env.ref('account.data_account_type_revenue')
        self.account = self.AccountObj.search([
            ('user_type_id', '=', self.account_type.id)
        ], limit=1)

        self.invoice_01 = self.InvoiceObj.create({
            'partner_id': self.env.ref('base.res_partner_12').id,
            'user_id': self.env.ref('base.user_demo').id,
            'payment_term_id': self.env.ref('account.account_payment_term').id,
            'type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0, {
                    'name': "Test",
                    'product_id': self.env.ref('product.consu_delivery_02').id,
                    'account_id': self.account.id,
                    'price_unit': 500,
                    'quantity': 5,
                }),
                (0, 0, {
                    'name': "Test",
                    'product_id': self.env.ref('product.consu_delivery_03').id,
                    'account_id': self.account.id,
                    'price_unit': 100,
                    'quantity': 5,
                }),
            ]
        })

    def test_split_invoice_line_quantity(self):
        line_to_split = self.invoice_01.invoice_line_ids[0]

        original_quantity = line_to_split.quantity
        wiz = self.SplitObj.with_context(
            active_ids=[self.invoice_01.id]).create({})
        wiz_line = wiz.line_ids.filtered(
            lambda r: r.origin_invoice_line_id == line_to_split)
        quantity_to_split = 1
        wiz_line.quantity_to_split = quantity_to_split
        new_invoice_id = wiz._split_invoice()
        # I check if a new invoice is created
        self.assertTrue(new_invoice_id is not False)
        # I check if there is one and only one line on the created invoice
        new_invoice = self.InvoiceObj.browse([new_invoice_id])[0]
        self.assertEqual(len(new_invoice.invoice_line_ids), 1)
        # I check the quantity on the new invoice line
        new_invoice_line = new_invoice.invoice_line_ids[0]
        self.assertEqual(new_invoice_line.quantity, quantity_to_split)
        # I check the remaining quantity on the original invoice
        self.assertEqual(
            line_to_split.quantity,
            original_quantity - quantity_to_split)

    def test_split_invoice_line_remove_line(self):
        line_to_split = self.invoice_01.invoice_line_ids[0]
        line_to_split.quantity = 1
        wiz = self.SplitObj.with_context(
            active_ids=[self.invoice_01.id]).create({})
        wiz_line = wiz.line_ids\
            .filtered(lambda r: (r.origin_invoice_line_id == line_to_split))
        quantity_to_split = 1
        wiz_line.quantity_to_split = quantity_to_split
        wiz._split_invoice()
        # I check that the line to split is deleted
        self.assertFalse(line_to_split.exists())

    def test_split_open_invoice(self):
        # I post the created invoice
        self.invoice_01.action_invoice_open()
        # Attempt to open the split wizard on an open invoice to check
        # if an exception is raised
        with self.assertRaises(UserError):
            self.SplitObj.with_context(
                active_ids=[self.invoice_01.id]).create({})
