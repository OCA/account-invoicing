# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase
from odoo.exceptions import ValidationError


class TestInvoiceFixedDiscount(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestInvoiceFixedDiscount, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test'})
        cls.tax = cls.env['account.tax'].create({
            'name': 'TAX 15%',
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'amount': 15.0,
        })
        cls.account_type = cls.env['account.account.type'].create({
            'name': 'Test',
            'type': 'receivable',
        })
        cls.account = cls.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST',
            'user_type_id': cls.account_type.id,
            'reconcile': True,
        })
        cls.invoice = cls.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'journal_id': cls.env['account.journal'].search(
                [('type', '=', 'sale')])[0].id,
            'partner_id': cls.partner.id,
            'account_id': cls.account.id,
        })
        cls.invoice_line = cls.env['account.invoice.line']
        cls.invoice_line1 = cls.invoice_line.create({
            'invoice_id': cls.invoice.id,
            'name': 'Line 1',
            'price_unit': 200.0,
            'account_id': cls.account.id,
            'invoice_line_tax_ids': [(6, 0, [cls.tax.id])],
            'quantity': 1,
        })

    def test_01_discounts(self):
        """ Tests multiple discounts in line with taxes."""
        # Apply a fixed discount
        self.invoice_line1.discount_fixed = 10.0
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice.amount_total, 218.50)
        # Try to add also a % discount
        with self.assertRaises(ValidationError):
            self.invoice_line1.write({'discount': 50.0})
        # Apply a % discount
        self.invoice_line1._onchange_discount_fixed()
        self.invoice_line1.discount_fixed = 0.0
        self.invoice_line1.discount = 50.0
        self.invoice_line1._onchange_discount()
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice.amount_total, 115.00)

    def test_02_discounts_multiple_lines(self):
        """ Tests multiple lines with mixed taxes and dicount types."""
        self.invoice_line2 = self.invoice_line.create({
            'invoice_id': self.invoice.id,
            'name': 'Line 1',
            'price_unit': 500.0,
            'account_id': self.account.id,
            'quantity': 1,
        })
        self.assertEqual(self.invoice_line2.price_subtotal, 500.0)
        # Add a fixed discount
        self.invoice_line2.discount_fixed = 100.0
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice_line2.price_subtotal, 400.0)
        self.assertEqual(self.invoice.amount_total, 630.0)
        self.invoice_line1.discount = 50.0
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice.amount_total, 515.0)
