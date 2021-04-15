# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestAccountBilling(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal_sale = cls.env["account.journal"].search([("type", "=", "sale")])[0]
        cls.invoice_model = cls.env["account.move"]
        cls.invoice_line_model = cls.env["account.move.line"]
        cls.billing_model = cls.env["account.billing"]
        cls.register_payments_model = cls.env["account.payment.register"]

        cls.partner_id = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.payment_term = cls.env.ref("account.account_payment_term_15days")
        cls.partner_agrolait = cls.env.ref("base.res_partner_2")
        cls.partner_china_exp = cls.env.ref("base.res_partner_3")
        cls.product = cls.env.ref("product.product_product_4")
        cls.currency_usd_id = cls.env.ref("base.USD").id
        cls.currency_eur_id = cls.env.ref("base.EUR").id
        cls.account_receivable = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
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
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_in"
        )
        cls.journal_bank = cls.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )

        cls.inv_1 = cls.create_invoice(
            cls, amount=100, currency_id=cls.currency_eur_id, partner=cls.partner_id.id
        )
        cls.inv_2 = cls.create_invoice(
            cls, amount=200, currency_id=cls.currency_eur_id, partner=cls.partner_id.id
        )
        cls.inv_3 = cls.create_invoice(
            cls, amount=300, currency_id=cls.currency_usd_id, partner=cls.partner_id.id
        )
        cls.inv_4 = cls.create_invoice(
            cls,
            amount=400,
            currency_id=cls.currency_eur_id,
            partner=cls.partner_china_exp.id,
        )
        cls.inv_5 = cls.create_invoice(
            cls, amount=500, currency_id=cls.currency_usd_id, partner=cls.partner_id.id
        )
        cls.inv_6 = cls.create_invoice(
            cls,
            amount=500,
            currency_id=cls.currency_usd_id,
            partner=cls.partner_id.id,
            invoice_type="in_refund",
        )

    def create_invoice(
        self,
        amount=None,
        invoice_type="out_invoice",
        currency_id=None,
        partner=None,
        account_id=None,
    ):
        """ Returns an open invoice """
        invoice = self.invoice_model.create(
            {
                "partner_id": partner or self.partner_agrolait.id,
                "currency_id": currency_id or self.currency_eur_id,
                "move_type": invoice_type,
                "invoice_date": fields.Date.today(),
                "invoice_payment_term_id": self.payment_term.id,
                "invoice_line_ids": [
                    [
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": amount,
                            "name": "something",
                            "account_id": self.account_revenue.id,
                        },
                    ]
                ],
            }
        )
        invoice.action_post()
        return invoice

    def create_payment(self, ctx):
        register_payments = self.register_payments_model.with_context(ctx).create(
            {
                "journal_id": self.journal_bank.id,
                "payment_method_id": self.payment_method_manual_in.id,
            }
        )
        return register_payments.action_create_payments()

    def test_1_invoice_partner(self):
        ctx = {
            "active_ids": [self.inv_1.id, self.inv_4.id],
            "bill_type": "out_invoice",
        }
        with self.assertRaises(ValidationError):
            self.billing_model.with_context(ctx).create({})

    def test_2_invoice_currency(self):
        ctx1 = {
            "active_ids": [self.inv_1.id, self.inv_3.id],
            "bill_type": "out_invoice",
        }
        with self.assertRaises(ValidationError):
            self.billing_model.with_context(ctx1).create({})
        # create billing directly
        self.billing_model.create({"partner_id": self.partner_agrolait.id})

    def test_3_validate_billing_state_not_open(self):
        ctx = {"active_model": "account.move", "active_ids": [self.inv_1.id]}
        self.create_payment(ctx)
        with self.assertRaises(ValidationError):
            self.billing_model.with_context(ctx).create({})

    def test_4_create_billing_from_selected_invoices(self):
        """ Create two invoices, post it and send context to Billing """
        ctx = {
            "active_model": "account.move",
            "active_ids": [self.inv_1.id, self.inv_2.id],
            "bill_type": "out_invoice",
        }
        customer_billing1 = self.billing_model.with_context(ctx).create({})
        self.assertEqual(customer_billing1.state, "draft")
        customer_billing1.with_context(ctx)._onchange_invoice_list()
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

        customer_billing2 = self.billing_model.with_context(ctx).create({})
        customer_billing2.with_context(ctx)._onchange_invoice_list()
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
                "partner_id": self.partner_id.id,
                "currency_id": self.currency_eur_id,
                "threshold_date": datetime.now(),
                "threshold_date_type": "invoice_date_due",
            }
        )
        bill1.threshold_date = bill1.threshold_date + relativedelta(months=12)
        bill1._onchange_invoice_list()
        bill1.validate_billing()
        self.assertEqual(bill1.invoice_related_count, 2)
        self.assertEqual(bill1.billing_line_ids.mapped("invoice_id.billing_ids"), bill1)

        # Create billing type - supplier
        bill2 = self.billing_model.create(
            {
                "bill_type": "in_invoice",
                "partner_id": self.partner_id.id,
                "currency_id": self.currency_usd_id,
                "threshold_date": datetime.now(),
                "threshold_date_type": "invoice_date_due",
            }
        )
        bill2.threshold_date = bill2.threshold_date + relativedelta(months=1)
        bill2._onchange_invoice_list()
        bill2.validate_billing()
        self.assertEqual(bill2.invoice_related_count, 1)

    def test_6_check_billing_from_bills(self):
        inv_1 = self.create_invoice(
            amount=100,
            currency_id=self.currency_eur_id,
            partner=self.partner_id.id,
            invoice_type="in_invoice",
        )
        if inv_1.state != "posted":
            inv_1.action_post()
        inv_2 = inv_1.copy()
        # Need to explicitly assign invoice date, not kept on copy
        inv_2.invoice_date = fields.Date.today()
        if inv_2.state != "posted":
            inv_2.action_post()
        ctx = {
            "active_model": "account.move",
            "active_ids": [inv_1.id, inv_2.id],
            "bill_type": "in_invoice",
        }
        vendor_billing = self.billing_model.with_context(ctx).create({})
        vendor_billing.with_context(ctx)._onchange_invoice_list()
