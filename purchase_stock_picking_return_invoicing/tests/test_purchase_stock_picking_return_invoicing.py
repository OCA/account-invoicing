# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseStockPickingReturnInvoicing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Add some defaults to let the test run without an accounts chart."""
        super(TestPurchaseStockPickingReturnInvoicing, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test journal", "type": "purchase", "code": "TEST_J"}
        )
        cls.account_payable_type = cls.env["account.account.type"].create(
            {
                "name": "Payable account type",
                "type": "payable",
                "internal_group": "liability",
            }
        )
        cls.account_expense_type = cls.env["account.account.type"].create(
            {
                "name": "Expense account type",
                "type": "other",
                "internal_group": "expense",
            }
        )
        cls.payable_account = cls.env["account.account"].create(
            {
                "name": "Payable Account",
                "code": "PAY",
                "user_type_id": cls.account_payable_type.id,
                "reconcile": True,
            }
        )
        cls.expense_account = cls.env["account.account"].create(
            {
                "name": "Expense Account",
                "code": "EXP",
                "user_type_id": cls.account_expense_type.id,
                "reconcile": False,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "is_company": True}
        )

        cls.partner.property_account_payable_id = cls.payable_account
        cls.product_categ = cls.env["product.category"].create(
            {"name": "Test category"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "test product",
                "categ_id": cls.product_categ.id,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "tpr1",
            }
        )
        cls.product.property_account_expense_id = cls.expense_account
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_qty": 5.0,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 10,
                            "date_planned": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )
        cls.po_line = cls.po.order_line
        cls.po.button_confirm()
        cls.po.button_approve()

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

    def test_initial_state(self):
        self.check_values(self.po_line, 0, 0, 0, 0, "no")

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
        self.assertAlmostEqual(inv_1.amount_untaxed_signed, -50, 2)

        # Return some items, after PO was invoiced
        return_wizard = self.env["stock.return.picking"].create({"picking_id": pick.id})
        return_wizard._onchange_picking_id()
        return_wizard.product_return_moves.write({"quantity": 2, "to_refund": True})
        return_pick = pick.browse(return_wizard.create_returns()["res_id"])
        return_pick.move_lines.write({"quantity_done": 2})
        return_pick.button_validate()
        self.check_values(self.po_line, 2, 3, 0, 5, "to invoice")
        # Make refund
        action2 = self.po.with_context(
            default_move_type="in_refund"
        ).action_create_invoice_refund()
        inv_2 = self.env["account.move"].browse(action2["res_id"])
        self.check_values(self.po_line, 2, 3, 2, 3, "invoiced")

        self.assertAlmostEqual(inv_2.amount_untaxed_signed, 20, 2)
        action = self.po.action_view_invoice()
        self.assertEqual(action["res_id"], inv_1.id)
        action2 = self.po.action_view_invoice_refund()
        self.assertEqual(action2["res_id"], inv_2.id)

    def test_purchase_stock_return_2(self):
        """Test a PO with received and returned qty, and invoiced after.

        Receive the PO, then do a partial return of the picking.
        Create a new invoice to get the bill for the remaining qty.
        Check that the invoicing status of the purchase, and quantities
        received and billed are correct throughout the process.
        """
        pick = self.po.picking_ids
        pick.move_lines.write({"quantity_done": 5})
        pick.button_validate()
        # Return some items before PO was invoiced
        return_wizard = self.env["stock.return.picking"].create({"picking_id": pick.id})
        return_wizard._onchange_picking_id()
        return_wizard.product_return_moves.write({"quantity": 2, "to_refund": True})
        return_pick = pick.browse(return_wizard.create_returns()["res_id"])
        return_pick.move_lines.write({"quantity_done": 2})
        return_pick.button_validate()
        self.check_values(self.po_line, 2, 3, 0, 0, "to invoice")
        # Make invoice
        action = self.po.action_create_invoice()
        inv_1 = self.env["account.move"].browse(action["res_id"])
        self.check_values(self.po_line, 2, 3, 0, 3, "invoiced")
        self.assertAlmostEqual(inv_1.amount_untaxed_signed, -30, 2)
