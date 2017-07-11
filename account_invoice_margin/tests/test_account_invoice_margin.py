# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase


class TestAccountInvoiceMargin(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceMargin, cls).setUpClass()
        cls.Product = cls.env['product.template']

        cls.journal = cls.env["account.journal"].create({
            "name": "Test journal",
            "type": "sale",
            "code": "TEST_J",
        })
        cls.account_type = cls.env["account.account.type"].create({
            "name": "Test account type",
            "type": "receivable",
        })
        cls.account = cls.env["account.account"].create({
            "name": "Test account",
            "code": "TEST_A",
            "user_type_id": cls.account_type.id,
            "reconcile": True,
        })
        cls.partner = cls.env["res.partner"].create({
            "name": "Test partner",
            "customer": True,
            "is_company": True,
        })
        cls.partner.property_account_receivable_id = cls.account
        cls.product_categ = cls.env["product.category"].create({
            "name": "Test category"
        })

        cls.product = cls.env["product.product"].create({
            "name": "test product",
            "categ_id": cls.product_categ.id,
            "uom_id": cls.env.ref('product.product_uom_unit').id,
            "uom_po_id": cls.env.ref('product.product_uom_unit').id,
            "default_code": "test-margin",
            "list_price": 200.00,
            "standard_price": 100.00,
        })
        cls.product.property_account_receivable_id = cls.account
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'date_invoice': '2017-06-19',
            'type': 'out_invoice',
            'currency_id': cls.env.user.company_id.currency_id.id,
            'account_id': cls.partner.property_account_receivable_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': cls.product.id,
                    'account_id':
                        cls.product.property_account_receivable_id.id,
                    'name': 'Test Margin',
                    'price_unit': cls.product.list_price,
                    'quantity': 10,
                    'purchase_price': cls.product.standard_price,
                })],
        })

    def test_invoice_margin(self):
        self.assertEqual(self.invoice.invoice_line_ids.purchase_price, 100.00)
        self.assertEqual(self.invoice.invoice_line_ids.margin, 1000.00)

        self.invoice.invoice_line_ids.discount = 50
        self.assertEqual(self.invoice.invoice_line_ids.margin, 0.0)

    def test_invoice_margin_uom(self):
        self.invoice.invoice_line_ids.write({
            'uom_id': self.env.ref('product.product_uom_dozen').id,
        })
        self.invoice.invoice_line_ids._onchange_uom_id()
        self.invoice.invoice_line_ids._onchange_product_id_margin()
        self.assertEqual(self.invoice.invoice_line_ids.margin, 12000.00)

    def test_invoice_refund(self):
        new_invoice = self.invoice.refund()
        self.assertEqual(new_invoice.invoice_line_ids.margin, 1000.00)
        self.assertEqual(new_invoice.invoice_line_ids.margin_signed, -1000.00)
