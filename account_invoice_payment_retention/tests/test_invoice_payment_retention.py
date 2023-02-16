# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, TransactionCase


class TestInvoicePaymentRetention(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestInvoicePaymentRetention, cls).setUpClass()

        cls.invoice_model = cls.env["account.move"]
        cls.payment_model = cls.env["account.payment"]
        cls.payment_register_model = cls.env["account.payment.register"]
        cls.register_view_id = "account.view_account_payment_register_form"
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product_3 = cls.env.ref("product.product_product_3")
        cls.account_receivable = cls.partner.property_account_receivable_id
        cls.account_retention = cls.env["account.account"].create(
            {
                "code": "RE",
                "name": "Retention Account",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_current_liabilities"
                ).id,
                "reconcile": True,
            }
        )
        cls.account_receivable_retention = cls.env["account.account"].create(
            {
                "code": "RE2",
                "name": "Retention Receivable Account",
                "user_type_id": cls.env.ref(
                    "account.data_account_type_current_liabilities"
                ).id,
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

        cls.account_revenue = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_revenue").id,
                ),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.account_expense = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_expenses").id,
                ),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.sale_journal = cls.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.purchase_journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )
        cls.cust_invoice = cls.invoice_model.create(
            {
                "name": "Test Customer Invoice",
                "move_type": "out_invoice",
                "journal_id": cls.sale_journal.id,
                "partner_id": cls.partner.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_3.id,
                            "quantity": 1.0,
                            "account_id": cls.account_revenue.id,
                            "name": "[PCSC234] PC Assemble SC234",
                            "price_unit": 500.00,
                        },
                    )
                ],
            }
        )
        cls.vendor_bill = cls.invoice_model.create(
            {
                "name": "Test Vendor Bill",
                "move_type": "in_invoice",
                "journal_id": cls.purchase_journal.id,
                "partner_id": cls.partner.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_product_3").id,
                            "quantity": 1.0,
                            "account_id": cls.account_expense.id,
                            "name": "[PCSC234] PC Assemble SC234",
                            "price_unit": 500.00,
                        },
                    )
                ],
            }
        )
        # New currency, 2X lower
        cls.company_currency = cls.cust_invoice.currency_id
        cls.company_currency.write(
            {
                "rate_ids": [
                    (
                        0,
                        0,
                        {
                            "name": fields.Date.today(),
                            "rate": 1,
                        },
                    )
                ]
            }
        )
        cls.currency_2x = cls.env["res.currency"].create(
            {
                "name": "2X",  # Foreign currency, 2 time
                "symbol": "X",
                "rate_ids": [
                    (
                        0,
                        0,
                        {
                            "name": fields.Date.today(),
                            "rate": cls.company_currency.rate * 2,
                        },
                    )
                ],
            }
        )

    def test_01_retention_account(self):
        """Retention account must be set as allow reconciliation"""
        self.env.company.retention_account_id = False
        self.account_retention.reconcile = False
        with self.assertRaises(ValidationError):
            self.env.company.retention_account_id = self.account_retention
        self.account_retention.reconcile = True
        self.env.company.retention_account_id = self.account_retention
        # Receivable
        self.env.company.retention_receivable_account_id = False
        self.account_receivable_retention.reconcile = False
        with self.assertRaises(ValidationError):
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
        with self.assertRaises(ValidationError):
            self.cust_invoice.payment_retention = "percent"
            self.cust_invoice.retention_method = "untax"
            self.cust_invoice.amount_retention = 101.0
        with self.assertRaises(ValidationError):
            self.cust_invoice.payment_retention = "percent"
            self.cust_invoice.retention_method = "total"
            self.cust_invoice.amount_retention = 101.0
        with self.assertRaises(ValidationError):
            self.cust_invoice.payment_retention = "amount"
            self.cust_invoice.amount_retention = 501.0
        # Now setup valid amount equal to 50
        self.cust_invoice.payment_retention = "percent"
        self.cust_invoice.retention_method = "untax"
        self.cust_invoice.amount_retention = 10
        self.assertEqual(self.cust_invoice.retention_amount_currency, 50.0)
        self.cust_invoice.action_post()
        # Register Payment
        ctx = {
            "active_ids": [self.cust_invoice.id],
            "active_id": self.cust_invoice.id,
            "active_model": "account.move",
            "default_enforce_payment_retention": False,
        }
        with Form(
            self.payment_register_model.with_context(**ctx), view=self.register_view_id
        ) as f:
            f.enforce_payment_retention = True
        payment_register = f.save()
        # Test enforce retention warning when retention amount/account not valid
        with self.assertRaises(ValidationError):
            payment_register.action_create_payments()

    def test_03_cust_invoice_payment_retention_normal(self):
        """Test 2 invoice retention and 1 retetnion return invoice"""
        self.cust_invoice2 = self.cust_invoice.copy({"name": "Test Invoice 2"})
        # Invoice 1, 10% = 50.0
        self.cust_invoice.payment_retention = "percent"
        self.cust_invoice.retention_method = "untax"
        self.cust_invoice.amount_retention = 10.0
        self.assertEqual(self.cust_invoice.retention_amount_currency, 50.0)
        self.cust_invoice.action_post()
        # Invoice 2, 100.0
        self.cust_invoice2.payment_retention = "amount"
        self.cust_invoice2.amount_retention = 100.0
        self.assertEqual(self.cust_invoice2.retention_amount_currency, 100.0)
        self.cust_invoice2.action_post()

        # Invoice 1 register payment
        ctx = {
            "active_ids": [self.cust_invoice.id],
            "active_id": self.cust_invoice.id,
            "active_model": "account.move",
        }
        with Form(
            self.payment_register_model.with_context(**ctx), view=self.register_view_id
        ) as f:
            f.enforce_payment_retention = True
            f.apply_payment_retention = True
        payment_register = f.save()
        self.assertEqual(payment_register.retention_amount_currency, 50.0)
        # Test enforce retention warning when retention amount/account not valid
        payment_dict = payment_register.action_create_payments()
        payment = self.payment_model.browse(payment_dict.get("res_id", False))
        self.assertEqual(payment.reconciled_invoice_ids, self.cust_invoice)
        payment_moves = payment.line_ids.mapped("move_id")

        # Invoice 2 register payment
        ctx = {
            "active_ids": [self.cust_invoice2.id],
            "active_id": self.cust_invoice2.id,
            "active_model": "account.move",
        }
        with Form(
            self.payment_register_model.with_context(**ctx), view=self.register_view_id
        ) as f:
            f.enforce_payment_retention = True
            f.apply_payment_retention = True
        payment_register = f.save()
        self.assertEqual(payment_register.retention_amount_currency, 100.0)
        # Test enforce retention warning when retention amount/account not valid
        payment_dict = payment_register.action_create_payments()
        payment = self.payment_model.browse(payment_dict.get("res_id", False))
        self.assertEqual(payment.reconciled_invoice_ids, self.cust_invoice2)
        payment_moves += payment.line_ids.mapped("move_id")

        # invoice 3, return retention
        view_id = "account.view_move_form"
        with Form(
            self.invoice_model.with_context(default_move_type="out_invoice"),
            view=view_id,
        ) as f:
            f.journal_id = self.sale_journal
            f.partner_id = self.partner
        cust_invoice3 = f.save()
        self.assertEqual(cust_invoice3.domain_retained_move_ids, payment_moves)
        #  Select retained moves
        with Form(
            cust_invoice3.with_context(check_move_validity=False), view=view_id
        ) as inv:
            for move in payment_moves:
                inv.retained_move_ids.add(move)
        cust_invoice3 = inv.save()
        total = sum(cust_invoice3.invoice_line_ids.mapped("price_unit"))
        cust_invoice3.write(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "/",
                            "debit": total,
                            "account_id": self.account_receivable.id,
                        },
                    )
                ]
            }
        )
        cust_invoice3.action_post()
        # After validate invoice, all retention is cleared
        cust_invoice3._onchange_domain_retained_move_ids()
        self.assertFalse(cust_invoice3.domain_retained_move_ids)

    def test_04_vendor_bill_payment_retention_currency(self):
        """Test 2 invoice retention and 1 retetnion return invoice"""
        self.vendor_bill2 = self.vendor_bill.copy({"name": "Test Bill 2"})
        # Invoice 1, 10% = 50.0
        self.vendor_bill.payment_retention = "percent"
        self.cust_invoice.retention_method = "untax"
        self.vendor_bill.amount_retention = 10.0
        self.assertEqual(self.vendor_bill.retention_amount_currency, 50.0)
        self.vendor_bill.action_post()
        # Invoice 2, 100.0
        self.vendor_bill2.currency_id = self.currency_2x
        self.vendor_bill2.payment_retention = "amount"
        self.vendor_bill2.amount_retention = 100.0
        self.assertEqual(self.vendor_bill2.retention_amount_currency, 100.0)
        self.vendor_bill2.invoice_date = fields.Date.today()
        self.vendor_bill2.action_post()

        # Invoice 1 register payment
        ctx = {
            "active_ids": [self.vendor_bill.id],
            "active_id": self.vendor_bill.id,
            "active_model": "account.move",
        }
        with Form(
            self.payment_register_model.with_context(**ctx), view=self.register_view_id
        ) as f:
            f.currency_id = self.currency_2x  # --> Change to 2x currency
            f.enforce_payment_retention = True
            f.apply_payment_retention = True
        payment_register = f.save()
        self.assertEqual(payment_register.retention_amount_currency, 100)

        # Test enforce retention warning when retention amount/account not valid
        payment_dict = payment_register.action_create_payments()
        payment = self.payment_model.browse(payment_dict.get("res_id", False))
        self.assertEqual(payment.reconciled_bill_ids, self.vendor_bill)
        payment_moves = payment.line_ids.mapped("move_id")

        # Invoice 2 register payment
        ctx = {
            "active_ids": [self.vendor_bill2.id],
            "active_id": self.vendor_bill2.id,
            "active_model": "account.move",
        }
        with Form(
            self.payment_register_model.with_context(**ctx), view=self.register_view_id
        ) as f:
            f.currency_id = self.currency_2x  # --> Change to 2x currency
            f.enforce_payment_retention = True
            f.apply_payment_retention = True
        payment_register = f.save()
        self.assertEqual(payment_register.retention_amount_currency, 100)

        # Test enforce retention warning when retention amount/account not valid
        payment_dict = payment_register.action_create_payments()
        payment = self.payment_model.browse(payment_dict.get("res_id", False))
        self.assertEqual(payment.reconciled_bill_ids, self.vendor_bill2)
        payment_moves += payment.line_ids.mapped("move_id")

        # invoice 3, return retention
        view_id = "account.view_move_form"
        with Form(
            self.invoice_model.with_context(default_move_type="in_invoice"),
            view=view_id,
        ) as f:
            # f.journal_id = self.purchase_journal
            f.partner_id = self.partner
        vendor_bill3 = f.save()
        self.assertEqual(vendor_bill3.domain_retained_move_ids, payment_moves)
        #  Select retained moves
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
        vendor_bill3.action_post()
        # After validate invoice, all retention is cleared
        vendor_bill3._onchange_domain_retained_move_ids()
        self.assertFalse(vendor_bill3.domain_retained_move_ids)

    def test_05_multi_invoice_payment(self):
        """Test multi invoice payment. Not allowed if retention"""
        # Test multi invoice payment, no retention
        self.invoice_normal1 = self.cust_invoice.copy({"name": "Normal 1"})
        self.invoice_normal1.action_post()
        self.invoice_normal2 = self.cust_invoice.copy({"name": "Normal 2"})
        self.invoice_normal2.action_post()
        self.invoice_normal3 = self.cust_invoice.copy({"name": "Normal 3"})
        self.invoice_normal3.action_post()
        ctx = {
            "active_ids": [self.invoice_normal1.id, self.invoice_normal2.id],
            "active_model": "account.move",
        }
        f = Form(
            self.payment_register_model.with_context(**ctx), view=self.register_view_id
        )
        payment_register = f.save()
        payment_register.action_create_payments()

        # Test multi invoice payment, with some retention, not allowed
        self.cust_invoice2 = self.cust_invoice.copy({"name": "Test Invoice 2"})
        self.cust_invoice3 = self.cust_invoice.copy({"name": "Test Invoice 3"})
        # Invoice 1, 10% = 50.0
        self.cust_invoice.payment_retention = "percent"
        self.cust_invoice.retention_method = "untax"
        self.cust_invoice.amount_retention = 10.0
        self.assertEqual(self.cust_invoice.retention_amount_currency, 50.0)
        self.cust_invoice.action_post()
        # Invoice 2, 5% = 25.0
        self.cust_invoice2.payment_retention = "percent"
        self.cust_invoice2.retention_method = "total"
        self.cust_invoice2.amount_retention = 5.0
        self.assertEqual(self.cust_invoice2.retention_amount_currency, 25.0)
        self.cust_invoice2.action_post()
        self.cust_invoice3.action_post()
        ctx = {
            "active_ids": [
                self.cust_invoice.id,
                self.cust_invoice2.id,
                self.cust_invoice3.id,
            ],
            "active_model": "account.move",
        }
        f = Form(
            self.payment_register_model.with_context(**ctx), view=self.register_view_id
        )
        payment_register = f.save()
        with self.assertRaises(UserError):
            payment_register.action_create_payments()
