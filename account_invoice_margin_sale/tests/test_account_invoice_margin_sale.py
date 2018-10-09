# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountInvoiceMargin(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceMargin, cls).setUpClass()
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
            "invoice_policy": "order",
            "list_price": 200.00,
            "standard_price": 100.00,
        })
        cls.product.property_account_receivable_id = cls.account
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'pricelist_id': cls.env.ref('product.list0').id,
            'order_line': [(0, 0, {
                'name': cls.product.name,
                'product_id': cls.product.id,
                'product_uom_qty': 1,
                'product_uom': cls.product.uom_id.id,
                'price_unit': 100.0
            })],
        })

    def test_invoice_sale_order(self):
        self.sale_order.action_confirm()
        self.sale_order.order_line.purchase_price = 500.00
        invoice_id = self.sale_order.action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.assertEqual(invoice.invoice_line_ids.purchase_price, 500.00)
