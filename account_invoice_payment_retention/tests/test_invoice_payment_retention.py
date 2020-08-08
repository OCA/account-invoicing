# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, SavepointCase


class TestInvoicePaymentRetention(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestInvoicePaymentRetention, cls).setUpClass()

        cls.invoice_model = cls.env["account.move"]
        cls.partner = cls.env.ref("base.res_partner_12")
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
        # Enable retention feature
        cls.env.user.groups_id += cls.env.ref(
            "account_invoice_payment_retention.group_payment_retention"
        )
        cls.env.company.retention_account_id = cls.account_retention

        cls.account_revenue = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )
        cls.account_expense = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_expenses").id,
                )
            ],
            limit=1,
        )
        cls.sale_journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        cls.purchase_journal = cls.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )
        cls.cust_invoice = cls.invoice_model.create(
            {
                "name": "Test Customer Invoice",
                "type": "out_invoice",
                "journal_id": cls.sale_journal.id,
                "partner_id": cls.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_product_3").id,
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
                "type": "in_invoice",
                "journal_id": cls.purchase_journal.id,
                "partner_id": cls.partner.id,
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

    def test_retention_account(self):
        """ Retention account must be set as allow reconciliation """
        self.env.company.retention_account_id = False
        self.account_retention.reconcile = False
        with self.assertRaises(ValidationError):
            self.env.company.retention_account_id = self.account_retention
        self.account_retention.reconcile = True
        self.env.company.retention_account_id = self.account_retention

    def test_invoice_payment_retention_errors(self):
        """ Test invoice retention amount warning
            Test enforce retention warning when no valid retention
        """
        # Test invoice retention amount calculation
        with self.assertRaises(ValidationError):
            self.cust_invoice.payment_retention = "percent"
            self.cust_invoice.amount_retention = 101.0
        with self.assertRaises(ValidationError):
            self.cust_invoice.payment_retention = "amount"
            self.cust_invoice.amount_retention = 501.0
        # Now setup valid amount equal to 50
        self.cust_invoice.payment_retention = "percent"
        self.cust_invoice.amount_retention = 10
        self.assertEqual(self.cust_invoice.retention_amount_currency, 50.0)
        self.cust_invoice.post()
        # Register Payment
        ctx = {
            "active_ids": [self.cust_invoice.id],
            "active_id": self.cust_invoice.id,
            "active_model": "account.move",
            "default_enforce_payment_retention": False,
        }
        PaymentWizard = self.env["account.payment"]
        view_id = "account.view_account_payment_invoice_form"
        with Form(PaymentWizard.with_context(ctx), view=view_id) as f:
            f.enforce_payment_retention = True
        payment = f.save()
        # Test enforce retention warning when retention amount/account not valid
        with self.assertRaises(ValidationError):
            payment.post()
            _ = payment.reconciled_invoice_ids  # Check reconciled

    def test_cust_invoice_payment_retention_normal(self):
        """ Test 2 invoice retention and 1 retetnion return invoice
        """
        self.cust_invoice2 = self.cust_invoice.copy({"name": "Test Invoice 2"})
        # Invoice 1, 10% = 50.0
        self.cust_invoice.payment_retention = "percent"
        self.cust_invoice.amount_retention = 10.0
        self.assertEqual(self.cust_invoice.retention_amount_currency, 50.0)
        self.cust_invoice.post()
        # Invoice 2, 100.0
        self.cust_invoice2.payment_retention = "amount"
        self.cust_invoice2.amount_retention = 100.0
        self.assertEqual(self.cust_invoice2.retention_amount_currency, 100.0)
        self.cust_invoice2.post()

        # Invoice 1 register payment
        ctx = {
            "active_ids": [self.cust_invoice.id],
            "active_id": self.cust_invoice.id,
            "active_model": "account.move",
        }
        PaymentWizard = self.env["account.payment"]
        view_id = "account.view_account_payment_invoice_form"
        with Form(PaymentWizard.with_context(ctx), view=view_id) as f:
            f.enforce_payment_retention = True
            f.apply_payment_retention = True
        payment = f.save()
        self.assertEqual(payment.retention_amount_currency, 50.0)
        # Test enforce retention warning when retention amount/account not valid
        payment.post()
        self.assertEqual(payment.reconciled_invoice_ids, self.cust_invoice)
        payment_moves = payment.move_line_ids.mapped("move_id")

        # Invoice 2 register payment
        ctx = {
            "active_ids": [self.cust_invoice2.id],
            "active_id": self.cust_invoice2.id,
            "active_model": "account.move",
        }
        PaymentWizard = self.env["account.payment"]
        view_id = "account.view_account_payment_invoice_form"
        with Form(PaymentWizard.with_context(ctx), view=view_id) as f:
            f.enforce_payment_retention = True
            f.apply_payment_retention = True
        payment = f.save()
        self.assertEqual(payment.retention_amount_currency, 100.0)
        # Test enforce retention warning when retention amount/account not valid
        payment.post()
        self.assertEqual(payment.reconciled_invoice_ids, self.cust_invoice2)
        payment_moves += payment.move_line_ids.mapped("move_id")

        # invoice 3, return retention
        ctx = {"default_type": "out_invoice"}
        view_id = "account.view_move_form"
        with Form(self.invoice_model.with_context(ctx), view=view_id) as f:
            f.journal_id = self.sale_journal
            f.partner_id = self.partner
        cust_invoice3 = f.save()
        res = cust_invoice3._onchange_domain_retained_move_ids()
        retained_move_ids = res["domain"]["retained_move_ids"][0][2]
        self.assertEqual(sorted(retained_move_ids), sorted(payment_moves.ids))
        #  Select retained moves
        with Form(cust_invoice3, view=view_id) as f:
            for move in payment_moves:
                f.retained_move_ids.add(move)
        cust_invoice3 = f.save()
        cust_invoice3.post()
        # After validate invoice, all retention is cleared
        res = cust_invoice3._onchange_domain_retained_move_ids()
        retained_move_ids = res["domain"]["retained_move_ids"][0][2]
        self.assertFalse(retained_move_ids)

    def test_vendor_bill_payment_retention_currency(self):
        """ Test 2 invoice retention and 1 retetnion return invoice
        """
        self.vendor_bill2 = self.vendor_bill.copy({"name": "Test Bill 2"})
        # Invoice 1, 10% = 50.0
        self.vendor_bill.payment_retention = "percent"
        self.vendor_bill.amount_retention = 10.0
        self.assertEqual(self.vendor_bill.retention_amount_currency, 50.0)
        self.vendor_bill.post()
        # Invoice 2, 100.0
        self.vendor_bill2.currency_id = self.currency_2x
        self.vendor_bill2.payment_retention = "amount"
        self.vendor_bill2.amount_retention = 100.0
        self.assertEqual(self.vendor_bill2.retention_amount_currency, 100.0)
        self.vendor_bill2.post()

        # Invoice 1 register payment
        ctx = {
            "active_ids": [self.vendor_bill.id],
            "active_id": self.vendor_bill.id,
            "active_model": "account.move",
        }
        PaymentWizard = self.env["account.payment"]
        view_id = "account.view_account_payment_invoice_form"
        with Form(PaymentWizard.with_context(ctx), view=view_id) as f:
            f.currency_id = self.currency_2x  # --> Change to 2x currency
            f.enforce_payment_retention = True
            f.apply_payment_retention = True
        payment = f.save()
        self.assertEqual(payment.retention_amount_currency, 100)
        # Test enforce retention warning when retention amount/account not valid
        payment.post()
        self.assertEqual(payment.reconciled_invoice_ids, self.vendor_bill)
        payment_moves = payment.move_line_ids.mapped("move_id")

        # Invoice 2 register payment
        ctx = {
            "active_ids": [self.vendor_bill2.id],
            "active_id": self.vendor_bill2.id,
            "active_model": "account.move",
        }
        PaymentWizard = self.env["account.payment"]
        view_id = "account.view_account_payment_invoice_form"
        with Form(PaymentWizard.with_context(ctx), view=view_id) as f:
            f.currency_id = self.currency_2x  # --> Change to 2x currency
            f.enforce_payment_retention = True
            f.apply_payment_retention = True
        payment = f.save()
        self.assertEqual(payment.retention_amount_currency, 100)
        # Test enforce retention warning when retention amount/account not valid
        payment.post()
        self.assertEqual(payment.reconciled_invoice_ids, self.vendor_bill2)
        payment_moves += payment.move_line_ids.mapped("move_id")

        # invoice 3, return retention
        ctx = {"default_type": "in_invoice"}
        view_id = "account.view_move_form"
        with Form(self.invoice_model.with_context(ctx), view=view_id) as f:
            f.journal_id = self.sale_journal
            f.partner_id = self.partner
        vendor_bill3 = f.save()
        res = vendor_bill3._onchange_domain_retained_move_ids()
        retained_move_ids = res["domain"]["retained_move_ids"][0][2]
        self.assertEqual(sorted(retained_move_ids), sorted(payment_moves.ids))
        #  Select retained moves
        with Form(vendor_bill3, view=view_id) as f:
            for move in payment_moves:
                f.retained_move_ids.add(move)
        vendor_bill3 = f.save()
        vendor_bill3.post()
        # After validate invoice, all retention is cleared
        res = vendor_bill3._onchange_domain_retained_move_ids()
        retained_move_ids = res["domain"]["retained_move_ids"][0][2]
        self.assertFalse(retained_move_ids)

    def test_multi_invoice_payment(self):
        """ Test multi invoice payment. Not allowed if retention
        """
        # Test multi invoice payment, no retention
        self.invoice_normal1 = self.cust_invoice.copy({"name": "Normal 1"})
        self.invoice_normal1.post()
        self.invoice_normal2 = self.cust_invoice.copy({"name": "Normal 2"})
        self.invoice_normal2.post()
        ctx = {
            "active_ids": [self.invoice_normal1.id, self.invoice_normal2.id],
            "active_model": "account.move",
        }
        PaymentWizard = self.env["account.payment.register"]
        view_id = "account.view_account_payment_form_multi"
        f = Form(PaymentWizard.with_context(ctx), view=view_id)
        payment = f.save()
        payment.create_payments()

        # Test multi invoice payment, with some retention, not allowed
        self.cust_invoice2 = self.cust_invoice.copy({"name": "Test Invoice 2"})
        # Invoice 1, 10% = 50.0
        self.cust_invoice.payment_retention = "percent"
        self.cust_invoice.amount_retention = 10.0
        self.assertEqual(self.cust_invoice.retention_amount_currency, 50.0)
        self.cust_invoice.post()
        self.cust_invoice2.post()
        ctx = {
            "active_ids": [self.cust_invoice.id, self.cust_invoice2.id],
            "active_model": "account.move",
        }
        f = Form(PaymentWizard.with_context(ctx), view=view_id)
        payment = f.save()
        with self.assertRaises(UserError):
            payment.create_payments()
