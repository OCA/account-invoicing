# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import SavepointCase


class TestInvoiceTripleDiscount(SavepointCase):

    @classmethod
    def setUpClass(self):
        super(TestInvoiceTripleDiscount, self).setUpClass()
        self.invoice_line_obj = self.env['account.invoice.line']
        self.sale_account = self.env.ref('account.a_sale')
        self.tax = self.env.ref('account_invoice_triple_discount.tax')
        self.invoice = self.env.ref('account_invoice_triple_discount.invoice')
        self.invoice_line1 = self.env.ref(
            'account_invoice_triple_discount.invoice_line1')

    def test_01_discounts(self):
        """ Tests multiple discounts in line with taxes """
        # Adds a first discount
        self.invoice_line1.discount = 50.0
        self.invoice_line1._compute_price()
        self.invoice.button_reset_taxes()
        self.assertEqual(self.invoice.amount_total, 115.0)
        # Adds a second discount over the price calculated before
        self.invoice_line1.discount2 = 40.0
        self.invoice_line1._compute_price()
        self.invoice.button_reset_taxes()
        self.assertEqual(self.invoice.amount_total, 69.0)
        # Adds a third discount over the price calculated before
        self.invoice_line1.discount3 = 50.0
        self.invoice_line1._compute_price()
        self.invoice.button_reset_taxes()
        self.assertEqual(self.invoice.amount_total, 34.5)
        # Deletes first discount
        self.invoice_line1.discount = 0.0
        self.invoice_line1._compute_price()
        self.invoice.button_reset_taxes()
        self.assertEqual(self.invoice.amount_total, 69.0)
        # Charge 5% over price:
        self.invoice_line1.discount = -5.0
        self.invoice_line1._compute_price()
        self.invoice.button_reset_taxes()
        self.assertEqual(self.invoice.amount_total, 72.45)

    def test_02_discounts_multiple_lines(self):
        """ Tests multiple lines with mixed taxes """
        self.invoice_line2 = self.invoice_line_obj.create({
            'invoice_id': self.invoice.id,
            'name': 'Line 1',
            'price_unit': 500.0,
            'account_id': self.sale_account.id,
            'quantity': 1,
        })
        self.assertEqual(self.invoice_line2.price_subtotal, 500.0)
        self.invoice_line2.discount3 = 50.0
        self.invoice_line2._compute_price()
        self.assertEqual(self.invoice_line2.price_subtotal, 250.0)
        self.assertEqual(self.invoice.amount_total, 480.0)
        self.invoice_line1.discount = 50.0
        self.invoice_line1._compute_price()
        self.invoice.button_reset_taxes()
        self.assertEqual(self.invoice.amount_total, 365.0)
