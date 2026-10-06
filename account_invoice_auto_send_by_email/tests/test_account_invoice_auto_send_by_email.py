# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from unittest import mock

from odoo.orm.commands import Command
from odoo.tests.common import TransactionCase


class TestAccountInvoiceAutoSendByEmail(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                queue_job__no_delay=True,
                lang=None,  # Avoid translation issues when checking errors
            )
        )

        cls.AccountMove = cls.env["account.move"]
        cls.env["res.partner"].search([]).invoice_sending_method = "manual"
        cls.company = cls.env.user.company_id
        cls.env["account.journal"].create(
            {"name": "Test sale journal", "type": "sale", "code": "tsj"}
        )
        cls.customer = cls.env["res.partner"].create(
            {"name": "Customer", "invoice_sending_method": "email"}
        )
        cls.receivable_account = cls.env["account.account"].search(
            [
                (
                    "account_type",
                    "=",
                    "asset_receivable",
                ),
                ("company_ids", "in", cls.env.company.id),
            ],
            limit=1,
        )
        cls.income_account = cls.env["account.account"].search(
            [
                (
                    "account_type",
                    "=",
                    "liability_current",
                ),
                ("company_ids", "in", cls.env.company.id),
            ],
            limit=1,
        )
        cls.bank = cls.env.ref("base.res_bank_1")
        cls.partner_bank = cls.env["res.partner.bank"].create(
            {
                "bank_id": cls.bank.id,
                "acc_number": "300.300.300",
                "acc_holder_name": "AccountHolderName",
                "partner_id": cls.company.partner_id.id,
            }
        )
        cls.invoice = cls.AccountMove.create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.customer.id,
                "partner_bank_id": cls.partner_bank.id,
                "line_ids": [
                    Command.create(
                        {
                            "quantity": 3,
                            "price_unit": 4.0,
                            "debit": 12,
                            "credit": 12,
                            "name": "Some service",
                            "account_id": cls.receivable_account.id,
                        }
                    ),
                    Command.create(
                        {
                            "debit": 12,
                            "credit": 12,
                            "name": "inv",
                            "account_id": cls.income_account.id,
                        }
                    ),
                ],
            }
        )
        cls.invoice.action_post()
        cls.invoice.write({"payment_state": "not_paid"})

    @mock.patch(
        "odoo.addons.base.models.ir_actions_report.IrActionsReport._render_qweb_pdf"
    )
    def test_send_email_invoice_cron(self, mocked):
        # We don't care about the content of the invoice report
        mocked.return_value = (b"Whatever gets printed", "pdf")
        moves = self.AccountMove.search(
            self.AccountMove._email_invoice_to_send_domain()
        )
        self.assertTrue(moves)
        self.assertIn(self.invoice, moves)
        self.AccountMove.cron_send_email_invoice()
        moves = self.AccountMove.search(
            self.AccountMove._email_invoice_to_send_domain()
        )
        self.assertFalse(moves)
        self.assertTrue(self.invoice.is_move_sent)

    def test_send_email_invoice_cron_other_company(self):
        """The customer's sending method is read for the invoice's company.

        Scenario:
            1. The customer is set to be sent invoices by email, but only in
               another company.
            2. The cron runs.
        Expected:
            - The invoice is not sent.
        """
        other_company = self.env["res.company"].create({"name": "Other company"})
        self.customer.invoice_sending_method = "manual"
        self.customer.with_company(other_company).invoice_sending_method = "email"
        self.assertNotIn(
            self.invoice,
            self.AccountMove.search(self.AccountMove._email_invoice_to_send_domain()),
        )
        self.AccountMove.cron_send_email_invoice()
        self.assertFalse(self.invoice.is_move_sent)

    def test_invoice_not_send_multiple_time(self):
        # Sending method is e-mail, but the invoice has already been sent
        self.invoice.is_move_sent = True
        res = self.invoice._execute_invoice_sent_wizard()
        self.assertEqual(res, "This invoice has already been sent.")
        # The invoice hasn't been sent yet, but the sending method is not e-mail
        self.invoice.is_move_sent = False
        self.customer.invoice_sending_method = "manual"
        res = self.invoice._execute_invoice_sent_wizard()
        self.assertEqual(res, "This invoice should not be sent by mail")
