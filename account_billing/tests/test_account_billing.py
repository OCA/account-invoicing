# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountBilling(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.billing_model = cls.env["account.billing"]
        cls.register_payments_model = cls.env["account.payment.register"]

        cls.payment_term = cls.env.ref("account.account_payment_term_15days")
        cls.partner_china_exp = cls.env.ref("base.res_partner_3")
        cls.product = cls.env.ref("product.product_product_4")

        cls.currency_usd_id = cls.env.ref("base.USD").id
        # Activate multi currency
        cls.env.ref("base.EUR").active = True
        cls.currency_eur_id = cls.env.ref("base.EUR").id

        cls.journal_bank = cls.company_data["default_journal_bank"]

        cls.inv_1 = cls._create_invoice(
            cls,
            move_type="out_invoice",
            invoice_amount=100,
            currency_id=cls.currency_eur_id,
            partner_id=cls.partner_a.id,
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )
        cls.inv_2 = cls._create_invoice(
            cls,
            move_type="out_invoice",
            invoice_amount=200,
            currency_id=cls.currency_eur_id,
            partner_id=cls.partner_a.id,
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )
        cls.inv_3 = cls._create_invoice(
            cls,
            move_type="out_invoice",
            invoice_amount=300,
            currency_id=cls.currency_usd_id,
            partner_id=cls.partner_a.id,
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )
        cls.inv_4 = cls._create_invoice(
            cls,
            move_type="out_invoice",
            invoice_amount=400,
            currency_id=cls.currency_eur_id,
            partner_id=cls.partner_china_exp.id,
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )
        cls.inv_5 = cls._create_invoice(
            cls,
            move_type="out_invoice",
            invoice_amount=500,
            currency_id=cls.currency_usd_id,
            partner_id=cls.partner_a.id,
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )
        cls.inv_6 = cls._create_invoice(
            cls,
            move_type="in_refund",
            invoice_amount=500,
            currency_id=cls.currency_usd_id,
            partner_id=cls.partner_a.id,
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )

    def create_payment(self, ctx):
        register_payments = self.register_payments_model.with_context(**ctx).create(
            {
                "journal_id": self.journal_bank.id,
                "payment_method_line_id": self.inbound_payment_method_line.id,
            }
        )
        return register_payments.action_create_payments()

    def test_1_invoice_partner(self):
        # Test difference partner
        invoices = self.inv_1 + self.inv_4
        with self.assertRaises(UserError):
            invoices.action_create_billing()

    def test_2_invoice_currency(self):
        # Test difference currency
        invoices = self.inv_1 + self.inv_3
        with self.assertRaises(UserError):
            invoices.action_create_billing()

    def test_3_validate_billing_state_not_open(self):
        ctx = {"active_model": "account.move", "active_ids": [self.inv_1.id]}
        self.create_payment(ctx)
        with self.assertRaises(UserError):
            self.inv_1.action_create_billing()

    def test_4_create_billing_from_selected_invoices(self):
        """Create two invoices, post it and send context to Billing"""
        ctx = {
            "active_model": "account.move",
            "active_ids": [self.inv_1.id, self.inv_2.id],
            "bill_type": "out_invoice",
        }
        invoices = self.inv_1 + self.inv_2
        action = invoices.action_create_billing()
        customer_billing1 = self.billing_model.browse(action["res_id"])
        self.assertEqual(customer_billing1.state, "draft")
        # Threshold Date error
        with self.assertRaises(ValidationError):
            customer_billing1.validate_billing()
        threshold_date_1 = customer_billing1.threshold_date + relativedelta(years=1)
        customer_billing1.threshold_date = threshold_date_1
        customer_billing1.validate_billing()
        self.assertEqual(customer_billing1.state, "billed")
        self.assertEqual(customer_billing1.invoice_related_count, 2)
        customer_billing1.invoice_relate_billing_tree_view()
        customer_billing1.action_cancel()
        customer_billing1.action_cancel_draft()

        invoices = self.inv_1 + self.inv_2
        action = invoices.action_create_billing()
        customer_billing2 = self.billing_model.browse(action["res_id"])
        threshold_date_2 = customer_billing2.threshold_date + relativedelta(years=1)
        customer_billing2.threshold_date = threshold_date_2
        customer_billing2.validate_billing()
        self.create_payment(ctx)
        with self.assertRaises(ValidationError):
            customer_billing2.action_cancel()

    def test_5_create_billing_directly(self):
        bill1 = self.billing_model.create(
            {
                "bill_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "currency_id": self.currency_eur_id,
                "threshold_date": datetime.now(),
                "threshold_date_type": "invoice_date_due",
            }
        )
        bill1.threshold_date = bill1.threshold_date + relativedelta(months=12)
        # No lines
        with self.assertRaises(UserError):
            bill1.validate_billing()

        bill1.compute_lines()

        self.assertEqual(bill1.invoice_related_count, 2)
        self.assertEqual(bill1.billing_line_ids.mapped("move_id.billing_ids"), bill1)

        # Create billing type - supplier
        bill2 = self.billing_model.create(
            {
                "bill_type": "in_invoice",
                "partner_id": self.partner_a.id,
                "currency_id": self.currency_usd_id,
                "threshold_date": datetime.now(),
                "threshold_date_type": "invoice_date_due",
            }
        )
        bill2.threshold_date = bill2.threshold_date + relativedelta(months=12)
        bill2.compute_lines()
        bill2.validate_billing()
        self.assertEqual(bill2.invoice_related_count, 1)

    def test_6_check_billing_from_bills(self):
        inv_1 = self._create_invoice(
            move_type="in_invoice",
            invoice_amount=100,
            currency_id=self.currency_eur_id,
            partner_id=self.partner_a.id,
            payment_term_id=self.payment_term.id,
            auto_validate=True,
        )
        inv_2 = inv_1.copy()
        # Need to explicitly assign invoice date, not kept on copy
        inv_2.invoice_date = fields.Date.today()
        if inv_2.state != "posted":
            inv_2.action_post()
        invoices = inv_1 + inv_2
        action = invoices.action_create_billing()
        self.billing_model.browse(action["res_id"])
