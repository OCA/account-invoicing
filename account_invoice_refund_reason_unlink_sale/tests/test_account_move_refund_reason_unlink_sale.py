# Copyright (C) 2022 ForgeFlow Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo.tests.common import TransactionCase


class TestAccountInvoiceRefundReasonUnlinkSale(TransactionCase):
    def test_unlink_refund(self):
        invoice_refund_obj = self.env["account.move.reversal"]
        partner3 = self.env.ref("base.res_partner_3")
        product = self.env["product.product"].create(
            {"name": "Test Product", "invoice_policy": "order"}
        )
        reason = self.env["account.move.refund.reason"].create(
            {"name": "Example reason", "unlink_so": True}
        )
        sale = self.env["sale.order"].create(
            {
                "partner_id": partner3.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        sale.action_confirm()
        wiz = self.env["sale.advance.payment.inv"]
        wiz = wiz.with_context(active_ids=sale.ids)
        wiz = wiz.create({"advance_payment_method": "delivered"})
        wiz.create_invoices()
        account_invoice_customer = self.env["account.move"].search(
            [("invoice_origin", "=", sale.name)]
        )
        account_invoice_customer.action_post()
        account_invoice_refund = invoice_refund_obj.with_context(
            active_model="account.move", active_ids=account_invoice_customer.ids
        ).create(
            dict(
                refund_method="refund",
                date=datetime.date.today(),
                reason_id=reason.id,
            )
        )
        account_invoice_refund.reverse_moves()
        reversal_move = account_invoice_customer.reversal_move_id
        reversal_move.action_post()
        self.assertFalse(reversal_move.invoice_line_ids.sale_line_ids)
