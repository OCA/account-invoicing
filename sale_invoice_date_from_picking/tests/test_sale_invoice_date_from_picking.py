# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestInvoiceDateFromPickingActualDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "list_price": 100.0,
            }
        )
        cls.env.company.picking_date_field_for_invoice_date = False

    def _create_sale_order(self, partner, product, quantity=1):
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": quantity,
                        }
                    )
                ],
            }
        )
        order.action_confirm()
        return order

    def _validate_picking(self, picking):
        picking.move_ids.quantity_done = picking.move_ids.product_uom_qty
        picking.action_confirm()
        picking.action_assign()
        picking.button_validate()

    def test_invoice_date_empty(self):
        order = self._create_sale_order(self.partner, self.product)
        picking = order.picking_ids[0]
        self._validate_picking(picking)
        invoice = order._create_invoices()
        self.assertFalse(invoice.invoice_date)

    def test_invoice_date_matches_date_done(self):
        date_done_field = self.env["ir.model.fields"].search(
            [
                ("model", "=", "stock.picking"),
                ("name", "=", "date_done"),
            ],
            limit=1,
        )
        self.env.company.picking_date_field_for_invoice_date = date_done_field
        order = self._create_sale_order(self.partner, self.product)
        picking = order.picking_ids[0]
        self._validate_picking(picking)
        invoice = order._create_invoices()
        picking_date = fields.Datetime.context_timestamp(
            order.with_context(tz=order.company_id.partner_id.tz), picking.date_done
        ).date()
        self.assertEqual(
            invoice.invoice_date,
            picking_date,
            "Invoice date should match picking's date_done.",
        )
