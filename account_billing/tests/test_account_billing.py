# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import Command, fields
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
            date_invoice=fields.Date.context_today(cls.env.user),
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )
        cls.inv_2 = cls._create_invoice(
            cls,
            move_type="out_invoice",
            invoice_amount=200,
            currency_id=cls.currency_eur_id,
            partner_id=cls.partner_a.id,
            date_invoice=fields.Date.context_today(cls.env.user),
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )
        cls.inv_3 = cls._create_invoice(
            cls,
            move_type="out_invoice",
            invoice_amount=300,
            currency_id=cls.currency_usd_id,
            partner_id=cls.partner_a.id,
            date_invoice=fields.Date.context_today(cls.env.user),
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )
        cls.inv_4 = cls._create_invoice(
            cls,
            move_type="out_invoice",
            invoice_amount=400,
            currency_id=cls.currency_eur_id,
            partner_id=cls.partner_china_exp.id,
            date_invoice=fields.Date.context_today(cls.env.user),
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )
        cls.inv_5 = cls._create_invoice(
            cls,
            move_type="out_invoice",
            invoice_amount=500,
            currency_id=cls.currency_usd_id,
            partner_id=cls.partner_a.id,
            date_invoice=fields.Date.context_today(cls.env.user),
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )
        cls.inv_6 = cls._create_invoice(
            cls,
            move_type="in_refund",
            invoice_amount=500,
            currency_id=cls.currency_usd_id,
            partner_id=cls.partner_a.id,
            date_invoice=fields.Date.context_today(cls.env.user),
            payment_term_id=cls.payment_term.id,
            auto_validate=True,
        )

    def _create_invoice_with_due_date(self, invoice_amount, invoice_date, date_due):
        """Return a posted invoice with an explicit due date.

        _create_invoice() does not accept a due date, so it is written
        afterwards. The payment term inherited from the partner has to be
        removed first, otherwise the due date is recomputed from it.
        """
        invoice = self._create_invoice(
            invoice_amount=invoice_amount,
            currency_id=self.currency_eur_id,
            partner_id=self.partner_a.id,
            date_invoice=invoice_date,
        )
        invoice.invoice_payment_term_id = False
        invoice.invoice_date_due = date_due
        invoice.action_post()
        return invoice

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
        # In case other modules change the default value of threshold_date_type
        customer_billing1.threshold_date_type = "invoice_date_due"
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
        # In case _compute_billing_ids is not triggered again after compute_lines.
        bill1.billing_line_ids.mapped("move_id")._compute_billing_ids()
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

    def test_account_billing_currency(self):
        inv_1 = self._create_invoice(
            move_type="in_invoice",
            invoice_amount=100,
            currency_id=self.currency_eur_id,
            partner_id=self.partner_a.id,
            payment_term_id=self.payment_term.id,
            auto_validate=True,
        )
        inv_2 = inv_1.copy()
        inv_2.invoice_date = fields.Date.today()
        inv_2.action_post()
        invoices = inv_1 + inv_2
        action = invoices.action_create_billing()
        customer_billing = self.billing_model.browse(action["res_id"])
        self.assertEqual(customer_billing.currency_id.id, self.currency_eur_id)
        self.assertEqual(self.env.company.currency_id.id, self.currency_usd_id)

    def test_7_record_rule_company_restriction(self):
        other_company = self.env["res.company"].create({"name": "Other Company"})
        billing_other = self.billing_model.with_company(other_company).create(
            {
                "bill_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "currency_id": self.currency_eur_id,
                "threshold_date": datetime.now(),
                "threshold_date_type": "invoice_date_due",
                "company_id": other_company.id,
            }
        )
        self.env.user.company_ids = [Command.set([self.env.company.id])]
        billing = self.billing_model.search([("id", "=", billing_other.id)])
        self.assertFalse(billing, "Billing from another company should not be visible")
        billing_with_sudo = self.billing_model.sudo().search(
            [("id", "=", billing_other.id)]
        )
        self.assertTrue(billing_with_sudo, "Sudo should bypass company record rule")

    def test_sort_billing_lines(self):
        inv_a = self._create_invoice_with_due_date(
            100,
            fields.Date.from_string("2024-04-03"),
            fields.Date.from_string("2024-05-04"),
        )
        inv_b = self._create_invoice_with_due_date(
            200,
            fields.Date.from_string("2024-04-01"),
            fields.Date.from_string("2024-05-02"),
        )
        inv_c = self._create_invoice_with_due_date(
            300,
            fields.Date.from_string("2024-04-02"),
            fields.Date.from_string("2024-05-01"),
        )
        inv_d = self._create_invoice_with_due_date(
            400,
            fields.Date.from_string("2024-04-02"),
            fields.Date.from_string("2024-05-01"),
        )
        invoices = inv_a + inv_b + inv_c + inv_d
        action = invoices.action_create_billing()
        billing = self.billing_model.browse(action["res_id"])
        # In case other modules change the default value of threshold_date_type
        billing.threshold_date_type = "invoice_date_due"
        billing._onchange_threshold_date_type()
        self.assertEqual(
            billing.billing_line_ids.mapped("move_id").ids,
            (inv_c + inv_d + inv_b + inv_a).ids,
        )

        # Onchange triggers re-sort
        billing.threshold_date_type = "invoice_date"
        billing._onchange_threshold_date_type()
        self.assertEqual(
            billing.billing_line_ids.mapped("move_id").ids,
            (inv_b + inv_c + inv_d + inv_a).ids,
        )
