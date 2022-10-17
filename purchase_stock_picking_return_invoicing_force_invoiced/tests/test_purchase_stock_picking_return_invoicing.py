# Copyright 2019 Eficent Business and IT Consulting Services
# Copyright 2022 NuoBiT Solutions, S.L. - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPurchaseStockPickingReturnInvoicing(TransactionCase):
    def setUp(self):
        super(TestPurchaseStockPickingReturnInvoicing, self).setUp()
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test partner",
                "is_company": True,
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "test product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                "default_code": "tpr1",
            }
        )
        self.po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_qty": 5.0,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": 10,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        self.po_line = self.po.order_line
        self.po.button_confirm()

    def check_values(
        self,
        po_line,
        qty_returned,
        qty_received,
        qty_refunded,
        qty_invoiced,
        invoice_status,
    ):
        self.assertAlmostEqual(po_line.qty_returned, qty_returned, 2)
        self.assertAlmostEqual(po_line.qty_received, qty_received, 2)
        self.assertAlmostEqual(po_line.qty_refunded, qty_refunded, 2)
        self.assertAlmostEqual(po_line.qty_invoiced, qty_invoiced, 2)
        self.assertEqual(po_line.order_id.invoice_status, invoice_status)

    def test_purchase_stock_return_1(self):
        """Test a PO with received, invoiced, returned and refunded qty.

        Receive and invoice the PO, then do a return of the picking.
        Check that the invoicing status of the purchase, and quantities
        received and billed are correct throughout the process.
        """
        # receive completely
        pick = self.po.picking_ids
        pick.move_lines.write({"quantity_done": 5})
        pick.button_validate()
        self.check_values(self.po_line, 0, 5, 0, 0, "to invoice")
        # Make invoice
        action = self.po.action_create_invoice()
        inv_1 = self.env["account.move"].browse(action["res_id"])
        self.check_values(self.po_line, 0, 5, 0, 5, "invoiced")
        # We set the force invoiced.
        self.po.button_done()
        self.po.force_invoiced = True
        self.assertAlmostEqual(inv_1.amount_untaxed_signed, -50, 2)
        # Return some items, after PO was invoiced
        return_wizard = self.env["stock.return.picking"].create({"picking_id": pick.id})
        return_wizard._onchange_picking_id()
        return_wizard.product_return_moves.write({"quantity": 2, "to_refund": True})
        return_pick = pick.browse(return_wizard.create_returns()["res_id"])
        return_pick.move_lines.write({"quantity_done": 2})
        return_pick.button_validate()
        self.assertEquals(self.po.invoice_status, "invoiced")
