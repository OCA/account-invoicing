# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPartnerLastInvoiceDate(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.account_move_model = cls.env["account.move"]

        cls.partner = cls.partner_model.create({"name": "Test Partner"})
        cls.partner_child = cls.partner_model.create(
            {
                "name": "Test Partner Child",
                "parent_id": cls.partner.id,
            }
        )

        cls.invoice = cls.account_move_model.create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 200.00,
                        },
                    ),
                ],
            }
        )
        cls.invoice.action_post()
        cls.invoice.write({"invoice_date": "2025-01-01"})
        cls.bill_1 = cls.account_move_model.create(
            {
                "partner_id": cls.partner.id,
                "move_type": "in_invoice",
                "invoice_date": "2025-01-02",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 200.00,
                        },
                    ),
                ],
            }
        )
        cls.bill_1.action_post()
        cls.bill_2 = cls.account_move_model.create(
            {
                "partner_id": cls.partner_child.id,
                "move_type": "in_invoice",
                "invoice_date": "2025-01-03",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 200.00,
                        },
                    ),
                ],
            }
        )
        cls.bill_2.action_post()

    def test_compute_last_invoice_bill_date(self):
        # Compute the field for both partners
        self.partner._compute_last_invoice_bill_date()
        self.partner_child._compute_last_invoice_bill_date()
        # Check the computed values
        self.assertEqual(self.partner.last_invoice_date, datetime.date(2025, 1, 1))
        self.assertEqual(self.partner.last_bill_date, datetime.date(2025, 1, 3))
        self.assertFalse(self.partner_child.last_invoice_date)
        self.assertEqual(self.partner_child.last_bill_date, datetime.date(2025, 1, 3))

        # Cancel the latest bill, which should affect the last bill date,
        # but not the last invoice date, and recompute the fields again
        self.bill_2.button_draft()
        self.bill_2.button_cancel()
        self.partner._compute_last_invoice_bill_date()
        self.partner_child._compute_last_invoice_bill_date()
        # Check the computed values after cancellation
        self.assertEqual(self.partner.last_invoice_date, datetime.date(2025, 1, 1))
        self.assertEqual(self.partner.last_bill_date, datetime.date(2025, 1, 2))
        self.assertFalse(self.partner_child.last_invoice_date)
        self.assertFalse(self.partner_child.last_bill_date)
