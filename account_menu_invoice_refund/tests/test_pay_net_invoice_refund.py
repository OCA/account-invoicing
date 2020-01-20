# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestAccountMenuInvoiceRefund(TransactionCase):
    def test_pay_net_invoice_refund(self):
        """By selecting 1 invoice and 1 refund document,
        I expect to net pay all document in one go."""
        invoice_line1_vals = [
            (
                0,
                0,
                {
                    "product_id": self.env.ref("product.product_product_2").id,
                    "quantity": 1.0,
                    "account_id": self.env["account.account"]
                    .search(
                        [
                            (
                                "user_type_id",
                                "=",
                                self.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    )
                    .id,
                    "name": "Product A",
                    "price_unit": 450.00,
                },
            )
        ]
        invoice_line2_vals = [
            (
                0,
                0,
                {
                    "product_id": self.env.ref("product.product_product_3").id,
                    "quantity": 1.0,
                    "account_id": self.env["account.account"]
                    .search(
                        [
                            (
                                "user_type_id",
                                "=",
                                self.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    )
                    .id,
                    "name": "Product B",
                    "price_unit": 200.00,
                },
            )
        ]
        # 2 products = 650
        invoice = self.env["account.move"].create(
            {
                "ref": "Test Customer Invoice",
                "type": "out_invoice",
                "journal_id": self.env["account.journal"]
                .search([("type", "=", "sale")], limit=1)
                .id,
                "partner_id": self.env.ref("base.res_partner_12").id,
                "invoice_line_ids": invoice_line1_vals + invoice_line2_vals,
            }
        )
        # refund 1 product = 200
        refund = self.env["account.move"].create(
            {
                "ref": "Test Customer Refund",
                "type": "out_refund",
                "journal_id": self.env["account.journal"]
                .search([("type", "=", "sale")], limit=1)
                .id,
                "partner_id": self.env.ref("base.res_partner_12").id,
                "invoice_line_ids": invoice_line2_vals,
            }
        )
        invoice.action_post()
        ctx = {"active_ids": [invoice.id, refund.id], "active_model": "account.move"}
        PaymentWizard = self.env["account.payment.register"]
        view_id = "account.view_account_payment_form_multi"
        with self.assertRaises(UserError):  # Test doc status exception
            Form(PaymentWizard.with_context(ctx), view=view_id)
        refund.action_post()
        # Finally, do the payment
        with Form(PaymentWizard.with_context(ctx), view=view_id) as f:
            f.group_payment = True
        payment = f.save()
        payment.create_payments()
        self.assertEqual(invoice.invoice_payment_state, "paid")
        self.assertEqual(refund.invoice_payment_state, "paid")
