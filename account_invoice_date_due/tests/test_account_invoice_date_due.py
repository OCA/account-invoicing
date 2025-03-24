# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form, common


class TestAccountInvoiceDateDue(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        group = cls.env.ref("account_invoice_date_due.allow_to_change_due_date")
        acc_group = cls.env.ref("account.group_account_manager")
        # Loose dependency on stock to avoid perm issues.
        # We don't really care about such permissions in this context!
        # Eg:
        # odoo.exceptions.AccessError:
        # You are not allowed to access 'Stock Valuation Layer'
        # (stock.valuation.layer) records.
        stock_group = (
            cls.env.ref("stock.group_stock_manager", False) or cls.env["res.groups"]
        )
        cls.user_w_access = cls.env["res.users"].create(
            {
                "name": "Test User w/ access",
                "login": "user_w_access",
                "email": "somebody@somewhere.com",
                "groups_id": [(6, 0, (group + acc_group + stock_group).ids)],
            }
        )
        # Create new user not allowed to change invoice due date
        cls.user_wo_access = cls.env["res.users"].create(
            {
                "name": "Test User wo/ access",
                "login": "user_wo_access",
                "groups_id": [(6, 0, (acc_group + stock_group).ids)],
            }
        )

        cls.sale_journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        move_form = Form(
            cls.env["account.move"].with_context(
                default_move_type="out_invoice",
                default_journal_id=cls.sale_journal.id,
            )
        )
        move_form.invoice_date = fields.Date.today()
        move_form.partner_id = cls.env["res.partner"].create({"name": "test partner"})

        with move_form.invoice_line_ids.new() as line_form:
            line_form.name = "move test"
            line_form.price_unit = 1000.0
        with move_form.invoice_line_ids.new() as line_form:
            line_form.name = "move test"
            line_form.price_unit = -1000.0
        cls.move = move_form.save()

    def _compare_records(self, rec1, rec2, ignore=None):
        diff_fields = []
        for field in rec1:
            if field in ignore:
                continue
            if rec1[field] != rec2[field]:
                diff_fields.append(field)
        return set(diff_fields)

    def test_invoice_date_due_is_editable(self):
        old_move_state = self.move.read()[0]
        move_edit_form = Form(self.move.with_user(self.user_w_access))
        ten_days_from_now = fields.Date.to_string(datetime.today() + timedelta(days=10))
        move_edit_form.invoice_date_due = ten_days_from_now
        self.move = move_edit_form.save()
        # Read all fields as sudo to get them independently of the user.
        # Other modules can add security groups in account.move fields
        self.assertEqual(
            self._compare_records(
                old_move_state,
                self.move.sudo().read()[0],
                ignore={"write_uid", "message_is_follower", "needed_terms"},
            ),
            # Assert only this field is changed
            {"invoice_date_due_payment_term", "invoice_date_due"},
        )
        self.assertEqual(
            fields.Date.to_string(self.move.invoice_date_due), ten_days_from_now
        )
        # Post and should remain editable
        self.move.action_post()
        old_move_state = self.move.read()[0]
        move_edit_form = Form(self.move.with_user(self.user_w_access))
        twenty_days_from_now = fields.Date.to_string(
            datetime.today() + timedelta(days=20)
        )
        move_edit_form.invoice_date_due = twenty_days_from_now
        self.move = move_edit_form.save()
        self.assertEqual(
            fields.Date.to_string(self.move.invoice_date_due), twenty_days_from_now
        )
        # Check that the change has been propagated to the corresponding invoice line
        self.assertEqual(
            len(
                self.move.line_ids.filtered(
                    lambda line: fields.Date.to_string(line.date_maturity)
                    == twenty_days_from_now
                    and line.account_id.account_type
                    in ("asset_receivable", "liability_payable")
                )
            ),
            1,
        )
        self.assertEqual(
            self._compare_records(
                old_move_state,
                self.move.sudo().read()[0],
                ignore={
                    "write_uid",
                    "message_is_follower",
                    "message_ids",
                    "needed_terms",
                    "hide_post_button",
                },
            ),
            # Assert only this field is changed
            {"invoice_date_due_payment_term", "invoice_date_due"},
        )

    def test_invoice_date_due_is_editable_w_payment_term(self):
        move_edit_form = Form(self.move.with_user(self.user_w_access))
        move_edit_form.invoice_payment_term_id = self.env.ref(
            "account.account_payment_term_15days"
        )
        self.move = move_edit_form.save()
        # Post and should remain editable even w/ payment term
        twenty_days_from_now = fields.Date.to_string(
            datetime.today() + timedelta(days=20)
        )
        self.move.action_post()
        old_move_state = self.move.read()[0]
        move_edit_form = Form(self.move.with_user(self.user_w_access))
        move_edit_form.invoice_date_due_payment_term = twenty_days_from_now
        self.move = move_edit_form.save()
        # Check that the change has been propagated to the corresponding invoice line
        self.assertEqual(
            len(
                self.move.line_ids.filtered(
                    lambda line: fields.Date.to_string(line.date_maturity)
                    == twenty_days_from_now
                    and line.account_id.account_type
                    in ("asset_receivable", "liability_payable")
                )
            ),
            1,
        )
        self.assertEqual(
            self._compare_records(
                old_move_state,
                self.move.sudo().read()[0],
                ignore={"write_uid", "message_is_follower", "message_ids"},
            ),
            # Assert only this field is changed
            {"invoice_date_due_payment_term", "invoice_date_due"},
        )

    def test_invoice_date_due_is_not_editable_for_user_wo_access(self):
        move_edit_form = Form(self.move.with_user(self.user_wo_access))
        ten_days_from_now = fields.Date.to_string(datetime.today() + timedelta(days=10))
        move_edit_form.invoice_date_due = ten_days_from_now
        self.move = move_edit_form.save()
        self.assertEqual(
            fields.Date.to_string(self.move.invoice_date_due), ten_days_from_now
        )  # Should be editable while in draft
        # Post and should not be editable for this user
        self.move.action_post()
        move_edit_form = Form(self.move.with_user(self.user_wo_access))
        twenty_days_from_now = fields.Date.to_string(
            datetime.today() + timedelta(days=20)
        )
        move_edit_form.invoice_date_due = twenty_days_from_now
        with self.assertRaisesRegex(
            UserError, "You are not allowed to change the due date."
        ):
            move_edit_form.save()
