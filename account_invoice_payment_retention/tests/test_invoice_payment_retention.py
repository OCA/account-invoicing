# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestInvoicePaymentRetention(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.payment_model = cls.env["account.payment"]
        cls.payment_register_model = cls.env["account.payment.register"]
        cls.register_view_id = "account.view_account_payment_register_form"
        cls.product_3 = cls.env.ref("product.product_product_3")
        cls.account_retention = cls.env["account.account"].create(
            {
                "code": "RE",
                "name": "Retention Account",
                "account_type": "liability_current",
                "reconcile": True,
            }
        )
        cls.account_receivable_retention = cls.env["account.account"].create(
            {
                "code": "RE2",
                "name": "Retention Receivable Account",
                "account_type": "liability_current",
                "reconcile": True,
            }
        )
        # Enable retention feature
        cls.env.user.groups_id += cls.env.ref(
            "account_invoice_payment_retention.group_payment_retention"
        )
        cls.env.company.retention_account_id = cls.account_retention
        cls.env.company.retention_receivable_account_id = (
            cls.account_receivable_retention
        )

        cls.cust_invoice = cls.init_invoice("out_invoice", amounts=[500.0])
        cls.vendor_bill = cls.init_invoice("in_invoice", amounts=[500.0])

    def test_01_retention_account(self):
        """Retention account must be set as allow reconciliation"""
        self.env.company.retention_account_id = False
        self.account_retention.reconcile = False
        err_msg = "Retention payable account should be set to allow Reconciliation"
        with self.assertRaisesRegex(ValidationError, err_msg):
            self.env.company.retention_account_id = self.account_retention
        self.account_retention.reconcile = True
        self.env.company.retention_account_id = self.account_retention
        # Receivable
        self.env.company.retention_receivable_account_id = False
        self.account_receivable_retention.reconcile = False
        err_msg = "Retention receivable account should be set to allow Reconciliation"
        with self.assertRaisesRegex(ValidationError, err_msg):
            self.env.company.retention_receivable_account_id = (
                self.account_receivable_retention
            )
        self.account_receivable_retention.reconcile = True
        self.env.company.retention_receivable_account_id = (
            self.account_receivable_retention
        )

    def test_02_invoice_payment_retention_errors(self):
        """Test invoice retention amount warning
        Test enforce retention warning when no valid retention
        """
        # Test invoice retention amount calculation
        self.cust_invoice.write(
            {
                "payment_retention": "percent",
                "retention_method": "untax",
                "amount_retention": 101.0,
            }
        )
        with self.assertRaisesRegex(
            ValidationError, "Retention must not exceed the total untaxed amount"
        ):
            self.cust_invoice.action_post()
        self.cust_invoice.button_draft()

        self.cust_invoice.write(
            {
                "payment_retention": "percent",
                "retention_method": "total",
                "amount_retention": 101.0,
            }
        )
        with self.assertRaisesRegex(
            ValidationError, "Retention must not exceed the total untaxed amount"
        ):
            self.cust_invoice.action_post()
        self.cust_invoice.button_draft()

        self.cust_invoice.write(
            {"payment_retention": "amount", "amount_retention": 501.0}
        )
        with self.assertRaisesRegex(
            ValidationError, "Retention must not exceed the total untaxed amount"
        ):
            self.cust_invoice.action_post()
        self.cust_invoice.button_draft()

        # Now setup valid amount equal to 50
        self.cust_invoice.write(
            {"payment_retention": "amount", "amount_retention": 50.0}
        )
        self.assertEqual(self.cust_invoice.retention_amount_currency, 50.0)
        self.cust_invoice.action_post()
        # Test enforce retention warning when retention amount/account not valid
        err_msg = (
            "This payment has retention, please make sure you fill "
            "in valid retaintion amount and retention account"
        )
        with self.assertRaisesRegex(ValidationError, err_msg):
            self.payment_register_model.with_context(
                active_model="account.move", active_ids=self.cust_invoice.ids
            ).create(
                {
                    "payment_date": fields.Date.today(),
                    "enforce_payment_retention": False,
                }
            )._create_payments()

    def test_03_cust_invoice_payment_retention_normal(self):
        """Test 2 invoice retention and 1 retetnion return invoice"""
        self.cust_invoice2 = self.cust_invoice.copy()
        # Invoice 1, 10% = 50.0
        self.cust_invoice.write(
            {
                "payment_retention": "percent",
                "retention_method": "untax",
                "amount_retention": 10.0,
            }
        )
        self.assertEqual(self.cust_invoice.retention_amount_currency, 50.0)
        self.cust_invoice.action_post()
        # Invoice 2, 100.0
        self.cust_invoice2.write(
            {
                "payment_retention": "amount",
                "amount_retention": 100.0,
            }
        )
        self.assertEqual(self.cust_invoice2.retention_amount_currency, 100.0)
        self.cust_invoice2.action_post()

        # Test register retention more than 1, it should error
        # Selected move(s) require payment retentions,
        # multi moves payment is not allowed.
        with self.assertRaises(UserError):
            self.payment_register_model.with_context(
                active_model="account.move",
                active_ids=(self.cust_invoice + self.cust_invoice2).ids,
            ).create(
                {
                    "payment_date": fields.Date.today(),
                    "enforce_payment_retention": True,
                }
            )._create_payments()

        # Invoice 1 register payment
        payment1 = (
            self.payment_register_model.with_context(
                active_model="account.move",
                active_ids=self.cust_invoice.ids,
            )
            .create(
                {
                    "payment_date": fields.Date.today(),
                    "enforce_payment_retention": True,
                }
            )
            ._create_payments()
        )

        # Invoice 2 register payment
        payment2 = (
            self.payment_register_model.with_context(
                active_model="account.move",
                active_ids=self.cust_invoice2.ids,
            )
            .create(
                {
                    "payment_date": fields.Date.today(),
                    "enforce_payment_retention": True,
                }
            )
            ._create_payments()
        )

        payment_moves = (payment1 + payment2).mapped("move_id")

        # invoice 3, return retention
        view_id = "account.view_move_form"
        cust_invoice3 = self.init_invoice("out_invoice")
        self.assertEqual(cust_invoice3.domain_retained_move_ids, payment_moves)
        self.assertFalse(cust_invoice3.invoice_line_ids)
        #  Select retained moves
        with Form(
            cust_invoice3.with_context(check_move_validity=False), view=view_id
        ) as inv:
            for move in payment_moves:
                inv.retained_move_ids.add(move)
        cust_invoice3 = inv.save()
        self.assertTrue(cust_invoice3.invoice_line_ids)
        cust_invoice3.action_post()

    def test_04_vendor_bill_payment_retention(self):
        """Test 2 bill retention and 1 retetnion return invoice"""
        self.vendor_bill2 = self.vendor_bill.copy()
        # Bill 1, 10% = 50.0
        self.vendor_bill.write(
            {
                "payment_retention": "percent",
                "retention_method": "untax",
                "amount_retention": 10.0,
            }
        )
        self.assertEqual(self.vendor_bill.retention_amount_currency, 50.0)
        self.vendor_bill.action_post()
        # Bill 2, 100.0
        self.vendor_bill2.write(
            {
                "payment_retention": "amount",
                "amount_retention": 100.0,
            }
        )
        self.assertEqual(self.vendor_bill2.retention_amount_currency, 100.0)
        self.vendor_bill2.invoice_date = fields.Date.today()
        self.vendor_bill2.action_post()

        # Bill1 register payment
        payment1 = (
            self.payment_register_model.with_context(
                active_model="account.move",
                active_ids=self.vendor_bill.ids,
            )
            .create(
                {
                    "payment_date": fields.Date.today(),
                    "enforce_payment_retention": True,
                }
            )
            ._create_payments()
        )

        payment2 = (
            self.payment_register_model.with_context(
                active_model="account.move",
                active_ids=self.vendor_bill2.ids,
            )
            .create(
                {
                    "payment_date": fields.Date.today(),
                    "enforce_payment_retention": True,
                }
            )
            ._create_payments()
        )

        payment_moves = (payment1 + payment2).mapped("move_id")

        # bill3, return retention
        vendor_bill3 = self.init_invoice("in_invoice")

        self.assertEqual(vendor_bill3.domain_retained_move_ids, payment_moves)
        self.assertFalse(vendor_bill3.invoice_line_ids)
        #  Select retained moves
        view_id = "account.view_move_form"
        with Form(
            vendor_bill3.with_context(check_move_validity=False), view=view_id
        ) as inv:
            for move in payment_moves:
                inv.retained_move_ids.add(move)
        vendor_bill3 = inv.save()
        vendor_bill3.write(
            {
                "invoice_date": fields.Date.today(),
            }
        )
        self.assertTrue(vendor_bill3.invoice_line_ids)
        vendor_bill3.action_post()
