# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountInvoicePricelist(SavepointCase):
    @classmethod
    def setUpClass(self):
        super(TestAccountInvoicePricelist, self).setUpClass()
        self.AccountInvoice = self.env["account.invoice"]
        self.ProductPricelist = self.env['product.pricelist']
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
            "name": "Test receivable account",
            "type": "receivable",
        })
        self.a_receivable = self.env["account.account"].create({
            "name": "Test receivable account",
            "code": "TEST_RA",
            "user_type_id": self.at_receivable.id,
            "reconcile": True,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'property_product_pricelist': 1,
            'property_account_receivable_id': self.a_receivable.id,
            'property_account_position_id': self.fiscal_position.id,
        })
        self.product = self.env['product.template'].create({
            'name': 'Product Test',
            'list_price': 100.00,
        })
        self.sale_pricelist_id = self.ProductPricelist.create({
            'name': 'Test Sale pricelist',
            'item_ids': [(0, 0, {
                    'applied_on': '1_product',
                    'compute_price': 'fixed',
                    'fixed_price': 300.00,
                    'product_tmpl_id': self.product.id,
                })],
        })
        self.invoice = self.AccountInvoice.create({
            'partner_id': self.partner.id,
            'account_id': self.a_receivable.id,
            'type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0, {
                    'account_id': self.a_receivable.id,
                    'product_id': self.product.product_variant_ids[:1].id,
                    'name': 'Test line',
                    'quantity': 1.0,
                    'price_unit': 100.00,
                }),
                (0, 0, {
                    'account_id': self.a_receivable.id,
                    'product_id': self.product.product_variant_ids[:2].id,
                    'name': 'Test line',
                    'quantity': 1.0,
                    'price_unit': 100.00,
                })
            ],
        })

    def test_account_invoice_pricelist(self):
        self.invoice._onchange_partner_id_account_invoice_pricelist()
        self.assertEqual(
            self.invoice.pricelist_id,
            self.invoice.partner_id.property_product_pricelist)

    def test_account_invoice_change_pricelist(self):
        self.invoice.pricelist_id = self.sale_pricelist_id.id
        self.invoice.button_update_prices_from_pricelist()
        invoice_line = self.invoice.invoice_line_ids[:1]
        self.assertEqual(invoice_line.price_unit, 300.00)
