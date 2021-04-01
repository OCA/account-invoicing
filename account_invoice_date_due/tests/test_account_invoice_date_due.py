# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests import Form, common


class TestAccountInvoiceDateDue(common.TransactionCase):
    def setUp(self):
        super().setUp()
        # Create new user allowed to change invoice due date
        group = self.env.ref("account_invoice_date_due.allow_to_change_due_date")
        acc_group = self.env.ref("account.group_account_manager")
        self.user_w_access = self.env["res.users"].create(
            {
                "name": "Test User w/ access",
                "login": "user_w_access",
                "groups_id": [(6, 0, [group.id, acc_group.id])],
            }
        )
        # Create new user not allowed to change invoice due date
        self.user_wo_access = self.env["res.users"].create(
            {
                "name": "Test User wo/ access",
                "login": "user_wo_access",
                "groups_id": [(6, 0, [acc_group.id])],
            }
        )
        account100 = self.env["account.account"].create(
            {
                "code": "100",
                "name": "Account 100",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        account300 = self.env["account.account"].create(
            {
                "code": "300",
                "name": "Account 300",
                "user_type_id": self.env.ref(
                    "account.data_account_type_other_income"
                ).id,
            }
        )
        move_form = Form(self.env["account.move"])
        move_form.date = fields.Date.today()
        with move_form.invoice_line_ids.new() as line_form:
            line_form.name = "move test"
            line_form.debit = 0.0
            line_form.credit = 1000.0
            line_form.account_id = account300
        with move_form.invoice_line_ids.new() as line_form:
            line_form.name = "move test"
            line_form.debit = 1000.0
            line_form.credit = 0.0
            line_form.account_id = account100
        self.move = move_form.save()

    def test_invoice_date_due_is_editable(self):
        move_edit_form = Form(self.move.with_user(self.user_w_access))
        ten_days_from_now = fields.Date.to_string(datetime.today() + timedelta(days=10))
        move_edit_form.invoice_date_due = ten_days_from_now
        self.move = move_edit_form.save()
        self.assertEquals(
            fields.Date.to_string(self.move.invoice_date_due), ten_days_from_now
        )
        # Post and should remain editable
        self.move.action_post()
        move_edit_form = Form(self.move.with_user(self.user_w_access))
        twenty_days_from_now = fields.Date.to_string(
            datetime.today() + timedelta(days=20)
        )
        move_edit_form.invoice_date_due = twenty_days_from_now
        self.move = move_edit_form.save()
        # Check that the change has been propagated to the corresponding invoice line
        self.assertEquals(
            len(
                self.move.line_ids.filtered(
                    lambda l: fields.Date.to_string(l.date_maturity)
                    == twenty_days_from_now
                    and l.account_id.user_type_id.type in ("receivable", "payable")
                )
            ),
            1,
        )

    def test_invoice_date_due_is_editable_w_payment_term(self):
        move_edit_form = Form(self.move.with_user(self.user_w_access))
        move_edit_form.invoice_payment_term_id = self.env.ref(
            "account.account_payment_term_15days"
        )
        self.move = move_edit_form.save()
        self.assertFalse(self.move.invoice_date_due)
        # Post and should remain editable even w/ payment term
        twenty_days_from_now = fields.Date.to_string(
            datetime.today() + timedelta(days=20)
        )
        self.move.action_post()
        move_edit_form = Form(self.move.with_user(self.user_w_access))
        move_edit_form.invoice_date_due_payment_term = twenty_days_from_now
        self.move = move_edit_form.save()
        # Check that the change has been propagated to the corresponding invoice line
        self.assertEquals(
            len(
                self.move.line_ids.filtered(
                    lambda l: fields.Date.to_string(l.date_maturity)
                    == twenty_days_from_now
                    and l.account_id.user_type_id.type in ("receivable", "payable")
                )
            ),
            1,
        )

    def test_invoice_date_due_is_not_editable_for_user_wo_access(self):
        move_edit_form = Form(self.move.with_user(self.user_wo_access))
        ten_days_from_now = fields.Date.to_string(datetime.today() + timedelta(days=10))
        move_edit_form.invoice_date_due = ten_days_from_now
        self.move = move_edit_form.save()
        self.assertEquals(
            fields.Date.to_string(self.move.invoice_date_due), ten_days_from_now
        )  # Should be editable while in draft
        # Post and should not be editable for this user
        self.move.action_post()
        move_edit_form = Form(self.move.with_user(self.user_wo_access))
        twenty_days_from_now = fields.Date.to_string(
            datetime.today() + timedelta(days=20)
        )
        with self.assertRaisesRegex(
            AssertionError, r"can't\swrite\son\sreadonly\sfield.*"
        ):
            move_edit_form.invoice_date_due = twenty_days_from_now
