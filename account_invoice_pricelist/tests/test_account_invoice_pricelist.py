# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import SavepointCase


class TestAccountInvoicePricelist(SavepointCase):
    @classmethod
    def setUpClass(self):
        super(TestAccountInvoicePricelist, self).setUpClass()
        self.AccountInvoice = self.env["account.invoice"]
        self.ProductPricelist = self.env['product.pricelist']
        self.ProductPricelistVersion = self.env['product.pricelist.version']
        self.ProductPricelistItem = self.env['product.pricelist.item']
        self.FiscalPosition = self.env['account.fiscal.position']
        self.fiscal_position = self.FiscalPosition.create({
            "name": "Test Fiscal Position",
            "active": True,
        })
        self.journal_sale = self.env["account.journal"].create({
            "name": "Test sale journal",
            "type": "sale",
            "code": "TEST_SJ",
        })
        self.at_receivable = self.env["account.account.type"].create({
            "name": "Test receivable account type",
            "code": "receivable_test",
            "close_method": "unreconciled",
            "report_type": "asset",
        })
        self.a_receivable = self.env["account.account"].create({
            "name": "Test receivable account",
            "code": "TEST_RA",
            "user_type": self.at_receivable.id,
            "type": "receivable",
            "reconcile": True,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'property_product_pricelist': 1,
            'property_account_receivable': self.a_receivable.id,
            'property_account_position': self.fiscal_position.id,
        })
        self.product = self.env['product.product'].create({
            'name': 'Product Test',
            'list_price': 100.00,
            'default_code': 'TEST0001',
        })
        # In 9.0 and later pricelist items are directly under pricelist,
        # each item having its own start and end date. In 8.0 and before
        # pricelists have versions, which have items... Moreover in 9.0 and
        # later fixed prices are supported out of the box while in 8.0 and
        # before these had to be simulated with subtracting -1 from the
        # rate and then adding the fixed price as a surcharge.
        self.sale_pricelist_id = self.ProductPricelist.create({
            'name': 'Test Sale pricelist',
            'currency_id': self.env.user.company_id.currency_id.id,
            'type': 'sale',
        })
        self.sale_pricelist_version_id = self.ProductPricelistVersion.create({
            'name': 'Test Sale pricelist Version',
            'pricelist_id': self.sale_pricelist_id.id,
        })
        self.sale_pricelist_item_id = self.ProductPricelistItem.create({
            'name': 'Test Sale pricelist Item',
            'price_version_id': self.sale_pricelist_version_id.id,
            'min_quantity': 1,
            'sequence': 5,
            'base': 1,
            'price_discount': -1.0,
            'price_surcharge': 300.00,
            'product_id': self.product.id,
        })
        # 8.0 invoice_line instead of invoice_line_ids
        self.invoice = self.AccountInvoice.create({
            'partner_id': self.partner.id,
            'account_id': self.a_receivable.id,
            'type': 'out_invoice',
            'invoice_line': [(0, 0, {
                'account_id': self.a_receivable.id,
                'product_id': self.product.id,
                'name': 'Test line',
                'quantity': 1.0,
                'price_unit': 100.00,
            })],
        })

    def test_onchange_partner_id(self):
        """Changing partner should set invoice pricelist to partner pricelist.
        """
        res = self.invoice.onchange_partner_id(
            'out_invoice', self.partner.id
        )
        self.assertEqual(
            res['value']['pricelist_id'],
            self.partner.property_product_pricelist.id)

    def test_product_id_change(self):
        """On change of product, price should be taken from pricelist."""
        res = self.invoice.invoice_line[0].with_context(
            pricelist_id=self.sale_pricelist_id.id,
        ).product_id_change(
            self.product.id,
            self.product.uom_id.id,
            qty=1,
            partner_id=self.partner.id
        )
        self.assertEqual(res['value']['price_unit'], 300.0)

    def test_button_update_prices_from_pricelist(self):
        """Update button should recompute prices."""
        self.invoice.pricelist_id = self.sale_pricelist_id
        self.invoice.button_update_prices_from_pricelist()
        self.assertEqual(
            self.invoice.invoice_line[0].price_unit,
            300.0
        )
        # Update should have no effect if state != draft:
        self.sale_pricelist_item_id.price_surcharge = 400.0
        self.invoice.state = 'open'  # just test, no need for workflow
        self.assertEqual(
            self.invoice.invoice_line[0].price_unit,
            300.0
        )
