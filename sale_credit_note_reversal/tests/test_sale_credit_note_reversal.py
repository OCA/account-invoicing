# Copyright 2024 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleCreditNoteReversal(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "consu"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    ),
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.order.action_confirm()
        cls.order.order_line[0].write({"qty_delivered": 5.0})
        cls.order._create_invoices()
        cls.invoice = cls.order.invoice_ids[0]
        cls.invoice.action_post()

    def move_reversal_wiz(self, move):
        wizard = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=[move.id])
            .create({"journal_id": move.journal_id.id})
        )
        return wizard

    def test_reversal_linked_to_order(self):
        """
        Revert the credit note and check the it is linked to the sales order.
        """
        self.assertEqual(self.order.order_line[0].qty_invoiced, 5.0)
        reversal_wizard = self.move_reversal_wiz(self.invoice)
        credit_note = self.env["account.move"].browse(
            reversal_wizard.reverse_moves()["res_id"]
        )
        credit_note.action_post()
        self.assertEqual(self.order.order_line[0].qty_invoiced, 0.0)
        second_reversal_wizard = self.move_reversal_wiz(credit_note)
        second_invoice = self.env["account.move"].browse(
            second_reversal_wizard.reverse_moves()["res_id"]
        )
        second_invoice.action_post()
        self.assertEqual(len(self.order.invoice_ids), 3.0)
        self.assertEqual(self.order.order_line[0].qty_invoiced, 5.0)
