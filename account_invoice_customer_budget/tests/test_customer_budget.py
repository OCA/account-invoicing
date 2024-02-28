# Copyright 2023 Akretion
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestBudgetInvoice(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.prepaid_revenue_account = cls.env["account.account"].create(
            {
                "name": "prepaid revenue account",
                "code": "PRAC",
                "account_type": "income",
                "deprecated": False,
                "company_id": cls.env.user.company_id.id,
            }
        )
        cls.budget_journal = cls.env["account.journal"].create(
            {
                "name": "Budget",
                "code": "BDG",
                "type": "sale",
                "company_id": cls.env.user.company_id.id,
                "is_budget": True,
            }
        )
        cls.budget_account_control_ids = [
            cls.company_data["default_account_receivable"].id,
            cls.prepaid_revenue_account.id,
            cls.env.user.company_id.account_sale_tax_id.mapped(
                "invoice_repartition_line_ids.account_id"
            ).id,
        ]
        cls.budget_journal.account_control_ids = [
            (6, 0, cls.budget_account_control_ids)
        ]

        move_form = Form(
            cls.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = cls.partner_a
        move_form.journal_id = cls.budget_journal
        with move_form.invoice_line_ids.new() as line_form:
            # Current price_unit is 1000.
            line_form.product_id = cls.product_b
            line_form.account_id = cls.prepaid_revenue_account
            line_form.price_unit = 2000
        cls.b_invoice = move_form.save()

        move_form = Form(
            cls.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = cls.partner_a
        with move_form.invoice_line_ids.new() as line_form:
            # Current price_unit is 400.
            line_form.product_id = cls.product_b
            line_form.price_unit = 400
        with move_form.invoice_line_ids.new() as line_form:
            # Current price_unit is -400 (budget comsumption).
            line_form.product_id = cls.product_b
            line_form.price_unit = -400
            line_form.budget_invoice_id = cls.b_invoice
            line_form.account_id = cls.prepaid_revenue_account
        cls.invoice = move_form.save()

    def test_budget_validation(self):
        # Test that budget can not be posted if there is no account_control_ids
        # defined in budget journal
        self.budget_journal.account_control_ids = False
        with self.assertRaises(UserError):
            self.b_invoice.action_post()
        self.budget_journal.account_control_ids = [
            (6, 0, self.budget_account_control_ids)
        ]
        self.b_invoice.action_post()

    def test_budget_consumption(self):
        self.b_invoice.action_post()
        self.invoice.action_post()
        self.assertEqual(1, len(self.b_invoice.budget_consumption_line_ids))
        self.assertEqual(
            self.b_invoice.budget_total_residual,
            self.b_invoice.amount_total + self.invoice.invoice_line_ids[1].price_total,
        )
        self.assertEqual(
            self.b_invoice.budget_total_consumption,
            self.invoice.invoice_line_ids[1].price_total,
        )

    def test_budget_over_consumption(self):
        self.b_invoice.action_post()
        self.invoice.invoice_line_ids[0].price_unit = 8000
        self.invoice.invoice_line_ids[1].price_unit = -8000
        with self.assertRaises(UserError):
            self.invoice.action_post()

    def test_budget_consumption_account(self):
        self.b_invoice.action_post()
        self.invoice.invoice_line_ids[0].price_unit = 8000
        self.invoice.invoice_line_ids[
            1
        ].account_id = self.product_b.property_account_income_id
        with self.assertRaises(UserError):
            self.invoice.action_post()
