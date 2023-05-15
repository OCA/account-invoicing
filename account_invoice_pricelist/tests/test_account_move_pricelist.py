# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.tests.common import Form


@tagged('post_install', '-at_install')
class TestAccountInvoicePricelist(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AccountInvoice = cls.env["account.move"]
        cls.AccountMoveLine = cls.env["account.move.line"]
        cls.ProductPricelist = cls.env['product.pricelist']
        cls.FiscalPosition = cls.env['account.fiscal.position']
        cls.fiscal_position = cls.FiscalPosition.create({
            "name": "Test Fiscal Position",
            "active": True,
        })
        cls.journal_sale = cls.env["account.journal"].create({
            "name": "Test sale journal",
            "type": "sale",
            "code": "TEST_SJ",
        })

        cls.a_receivable = cls.env["account.account"].create({
            "name": "Test receivable account",
            "code": 4111100,
            "account_type": 'asset_receivable',
            "reconcile": True,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'property_product_pricelist': 1,
            'property_account_receivable_id': cls.a_receivable.id,
            'property_account_position_id': cls.fiscal_position.id,
        })
        cls.product = cls.env['product.template'].create({
            'name': 'Product Test',
            'list_price': 100.00,
        })
        cls.sale_pricelist_id = cls.ProductPricelist.create({
            'name': 'Test Sale pricelist',
            'item_ids': [(0, 0, {
                    'applied_on': '1_product',
                    'compute_price': 'fixed',
                    'fixed_price': 300.00,
                    'product_tmpl_id': cls.product.id,
                })],
        })

        cls.invoice = cls.AccountInvoice.create({
            'partner_id': cls.partner.id,
            'move_type': 'out_invoice',
        })

        cls.invoice_line_ids = [
            (0, 0, {
                'product_id': cls.product.product_variant_ids[:1],
                'name': 'Test line',
                'quantity': 1.0,
                'price_unit': 100.00,
            }),
            (0, 0, {
                'product_id': cls.product.product_variant_ids[:2],
                'name': 'Test line',
                'quantity': 1.0,
                'price_unit': 100.00,
            })
        ]

        move_form = Form(cls.invoice)
        for line in cls.invoice_line_ids:
            with move_form.invoice_line_ids.new() as line_form:
                line_form.name = 'test line'
                line_form.product_id = line[2]['product_id']
                line_form.quantity = line[2]['quantity']
                line_form.price_unit = line[2]['price_unit']
            move_form.save()

    def test_account_invoice_pricelist(self):
        self.invoice._onchange_partner_id_account_invoice_pricelist()
        self.assertEqual(self.invoice.pricelist_id, self.invoice.partner_id.property_product_pricelist)

    def test_account_invoice_change_pricelist(self):
        self.invoice.pricelist_id = self.sale_pricelist_id.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 300.00)

