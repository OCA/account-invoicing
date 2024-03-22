# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import Form, SavepointCase


class TestAccountInvoiceUpdateStockValuation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product = cls.env.ref("product.product_product_6")
        cls.unit = cls.env.ref("uom.product_uom_unit")
        cls.dozen = cls.env.ref("uom.product_uom_dozen")

    def test_update_stock_valuation_from_invoice(self):
        purchase = self._create_purchase_order(
            self.partner, self.product, qty=1, uom=self.unit
        )
        invoice = self._create_invoice_from_purchase(purchase)
        invoice_line = invoice.invoice_line_ids[0].with_context(
            check_move_validity=False
        )
        invoice_line.price_unit += 10.0
        invoice._recompute_dynamic_lines()
        self.assertFalse(invoice_line.stock_valuation_ok)
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        invoice_line._compute_stock_valuation_ok()
        self.assertTrue(invoice_line.stock_valuation_ok)
        svl = self.env["stock.valuation.layer"].search(
            [
                ("product_id", "=", invoice_line.product_id.id),
                ("account_move_id", "=", invoice.id),
                ("company_id", "=", invoice_line.company_id.id),
                ("value", "=", invoice_line.price_unit),
            ]
        )
        self.assertTrue(svl)

    def test_update_stock_valuation_invoice_different_uom_purchase(self):
        # purchase order with 12 units
        # invoice with 1 Dozen
        purchase = self._create_purchase_order(
            self.partner, self.product, qty=12, uom=self.unit
        )
        invoice = self._create_invoice_from_purchase(purchase)
        invoice_line = invoice.invoice_line_ids[0].with_context(
            check_move_validity=False
        )
        invoice_line.update(
            {
                "price_unit": (invoice_line.price_unit * 12.0) + 10.0,
                "quantity": 1,
                "product_uom_id": self.dozen.id,
            }
        )
        invoice._recompute_dynamic_lines()
        self.assertFalse(invoice_line.stock_valuation_ok)
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        invoice_line._compute_stock_valuation_ok()
        self.assertTrue(invoice_line.stock_valuation_ok)
        svl = self.env["stock.valuation.layer"].search(
            [
                ("product_id", "=", invoice_line.product_id.id),
                ("quantity", "=", 12.0),
                ("uom_id", "=", self.unit.id),
                ("value", "=", invoice_line.price_unit),
                ("account_move_id", "=", invoice.id),
                ("company_id", "=", invoice_line.company_id.id),
            ]
        )
        self.assertTrue(svl)
        self.assertEqual(svl.unit_cost, 750.83)

    def test_update_stock_valuation_invoice_same_uom_purchase(self):
        # purchase order with 1 Dozen
        # invoice with 1 Dozen
        purchase = self._create_purchase_order(
            self.partner, self.product, qty=1, uom=self.dozen
        )
        invoice = self._create_invoice_from_purchase(purchase)
        invoice_line = invoice.invoice_line_ids[0].with_context(
            check_move_validity=False
        )
        invoice_line.price_unit += 10.0
        invoice._recompute_dynamic_lines()
        self.assertFalse(invoice_line.stock_valuation_ok)
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        invoice_line._compute_stock_valuation_ok()
        self.assertTrue(invoice_line.stock_valuation_ok)
        svl = self.env["stock.valuation.layer"].search(
            [
                ("product_id", "=", invoice_line.product_id.id),
                ("quantity", "=", 12.0),
                ("uom_id", "=", self.unit.id),
                ("value", "=", invoice_line.price_unit),
                ("account_move_id", "=", invoice.id),
                ("company_id", "=", invoice_line.company_id.id),
            ]
        )
        self.assertTrue(svl)
        self.assertEqual(svl.unit_cost, 750.83)

    def test_reset_to_draft_invoice(self):
        purchase = self._create_purchase_order(
            self.partner, self.product, qty=1, uom=self.unit
        )
        invoice = self._create_invoice_from_purchase(purchase)
        invoice_line = invoice.invoice_line_ids[0].with_context(
            check_move_validity=False
        )
        invoice_line.price_unit += 10.0
        invoice._recompute_dynamic_lines()
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        invoice_line._compute_stock_valuation_ok()
        invoice.button_draft()
        svl = self.env["stock.valuation.layer"].search(
            [
                ("account_move_id", "=", invoice.id),
                ("company_id", "=", invoice.company_id.id),
            ]
        )
        self.assertFalse(svl)

    def _create_purchase_order(self, partner, product, qty, uom):
        po = Form(self.env["purchase.order"])
        po.partner_id = partner
        with po.order_line.new() as po_line:
            po_line.product_id = product
            po_line.product_qty = qty
            po_line.product_uom = uom
        return po.save()

    def _create_invoice_from_purchase(self, purchase):
        purchase.button_confirm()
        purchase.picking_ids.move_lines.move_line_ids.qty_done = 1.0
        purchase.picking_ids._action_done()
        purchase.order_line.qty_received = 1.0
        purchase.action_create_invoice()
        return purchase.invoice_ids[0].with_context(check_move_validity=False)
