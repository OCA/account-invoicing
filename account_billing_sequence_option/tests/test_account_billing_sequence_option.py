# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestBillingSequenceOption(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.billing_model = cls.env["account.billing"]
        cls.move_model = cls.env["account.move"]
        cls.billing_seq_opt = cls.env.ref(
            "account_billing_sequence_option.billing_sequence_option"
        )
        cls.product = cls.env.ref("product.product_product_4")
        cls.partner = cls.env.ref("base.res_partner_2")

        cls.inv_1 = cls.create_invoice(cls)

    def create_invoice(self, move_type="out_invoice"):
        """Returns an open invoice"""
        invoice = self.move_model.create(
            {
                "partner_id": self.partner.id,
                "move_type": move_type,
                "invoice_date": "2000-01-01",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                            "name": "something",
                            "tax_ids": [],
                        }
                    )
                ],
            }
        )
        invoice.action_post()
        return invoice

    def test_account_billing_sequence_options(self):
        """test with and without sequence option activated"""
        # With sequence option
        self.billing_seq_opt.use_sequence_option = True
        ctx = {
            "active_model": "account.move",
            "active_ids": [self.inv_1.id],
            "bill_type": "out_invoice",
        }
        customer_billing = self.billing_model.with_context(**ctx).create({})
        customer_billing.with_context(**ctx)._onchange_invoice_list()
        self.assertFalse(customer_billing.name)
        customer_billing.validate_billing()
        self.assertIn("B/", customer_billing.name)
        # Without sequence option
        self.billing_seq_opt.use_sequence_option = False
        ctx = {
            "active_model": "account.move",
            "active_ids": [self.inv_1.id],
            "bill_type": "out_invoice",
        }
        customer_billing_2 = self.billing_model.with_context(**ctx).create({})
        customer_billing_2.with_context(**ctx)._onchange_invoice_list()
        self.assertFalse(customer_billing_2.name)
        customer_billing_2.validate_billing()
        self.assertNotIn("B/", customer_billing_2.name)
