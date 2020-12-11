# Copyright (C) 2020 - TODAY, Elego Software Solutions GmbH, Berlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestAccountApprovalProcess(AccountingTestCase):
    def setUp(self):
        super().setUp()

        self.account_expense = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_expenses").id,
                )
            ],
            limit=1,
        )
        self.account_receivable = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )

        product = self.env.ref("product.product_product_8")  # iMac $ 1299

        self.vendor_bill = self.env["account.invoice"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "type": "in_invoice",
                "account_id": self.account_receivable.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "name": product.display_name,
                            "quantity": 1.0,
                            "price_unit": product.standard_price,
                            "account_id": self.account_expense.id,
                        },
                    )
                ],
            }
        )

        self.vendor_bill._onchange_partner_id()

        self.vendor_bill.invoice_line_ids._onchange_product_id()
        self.vendor_bill.invoice_line_ids._onchange_account_id()

    def test_00_department_ids(self):
        template = self.env.ref(
            "account_approval_process.email_template_request_approval"
        )
        self.env.user.company_id.account_approval_process_ids = [
            (
                0,
                0,
                {
                    "invoice_type": "in_invoice",
                    "name": "Test 1",
                    "validation_amount_from": 0,
                    "email_template_id": template.id,
                    "department_ids": [(4, self.env.ref("hr.dep_management").id)],
                },
            )
        ]

        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertTrue(self.vendor_bill.approval_needed)
        self.assertTrue(self.vendor_bill.approval_authorized)

        self.vendor_bill.action_invoice_request_approval()
        self.vendor_bill.action_invoice_approve()
        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertFalse(self.vendor_bill.approval_requested)

        self.vendor_bill.action_invoice_open()
        self.assertEqual(self.vendor_bill.state, "open")

        self.assertFalse(self.vendor_bill.approval_needed)
        self.assertFalse(self.vendor_bill.approval_authorized)

    def test_01_manager_of_department_ids(self):
        template = self.env.ref(
            "account_approval_process.email_template_request_approval"
        )
        self.env.ref("hr.dep_administration").manager_id = self.env.user.id
        self.env.user.company_id.account_approval_process_ids = [
            (
                0,
                0,
                {
                    "invoice_type": "in_invoice",
                    "name": "Test 1",
                    "validation_amount_from": 0,
                    "email_template_id": template.id,
                    "manager_of_department_ids": [
                        (4, self.env.ref("hr.dep_administration").id)
                    ],
                },
            )
        ]

        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertTrue(self.vendor_bill.approval_needed)
        self.assertTrue(self.vendor_bill.approval_authorized)

        self.vendor_bill.action_invoice_request_approval()
        self.vendor_bill.action_invoice_approve()
        self.assertEqual(self.vendor_bill.state, "draft")
        self.assertFalse(self.vendor_bill.approval_requested)

        self.vendor_bill.action_invoice_open()
        self.assertEqual(self.vendor_bill.state, "open")

        self.assertFalse(self.vendor_bill.approval_needed)
        self.assertFalse(self.vendor_bill.approval_authorized)
