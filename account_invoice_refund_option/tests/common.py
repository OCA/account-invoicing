from odoo.tests import common


class AccountInvoiceRefundOptionTest(common.TransactionCase):
    """Base class - Test the Account Invoice Refund Option."""

    def setUp(self):
        super().setUp()
        # Useful models
        self.account_move_obj = self.env["account.move"]
        self.account_move_reversal_obj = self.env["account.move.reversal"]

        self.payment_term = self.env.ref("account.account_payment_term_advance")
        self.journalrec = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        self.partner3 = self.env.ref("base.res_partner_3")
        account_id = (
            self.env["account.account"]
            .search([("account_type", "=", "income")], limit=1)
            .id
        )

        self.move_line_data = [
            (
                0,
                0,
                {
                    "product_id": self.env.ref("product.product_product_1").id,
                    "quantity": 40.0,
                    "account_id": account_id,
                    "name": "product test 1",
                    "discount": 10.00,
                    "price_unit": 2.27,
                },
            ),
            (
                0,
                0,
                {
                    "product_id": self.env.ref("product.product_product_2").id,
                    "quantity": 21.0,
                    "account_id": account_id,
                    "name": "product test 2",
                    "discount": 10.00,
                    "price_unit": 2.77,
                },
            ),
        ]
