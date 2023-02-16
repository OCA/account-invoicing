# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import mock

from odoo.tests.common import SavepointCase


class TestAccountInvoiceAutoSendByEmail(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_queue_job_no_delay=True
            )
        )

        cls.AccountMove = cls.env["account.move"]
        cls.AccountMove.search([]).write({"transmit_method_code": ""})
        cls.company = cls.env.user.company_id
        cls.transmit_method = cls.env.ref("account_invoice_transmit_method.mail")
        cls.env["account.journal"].create(
            {"name": "Test sale journal", "type": "sale", "code": "tsj"}
        )
        cls.customer = cls.env.ref("base.res_partner_1")
        cls.receivable_account = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_receivable").id,
                ),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.income_account = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_current_liabilities").id,
                ),
                ("company_id", "=", cls.env.company.id),
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
                "transmit_method_id": cls.transmit_method.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "quantity": 3,
                            "price_unit": 4.0,
                            "debit": 12,
                            "credit": 0,
                            "name": "Some service",
                            "account_id": cls.receivable_account.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "debit": 0,
                            "credit": 12,
                            "name": "inv",
                            "account_id": cls.income_account.id,
                        },
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
        self.assertEqual(len(moves), 1)
        self.AccountMove.cron_send_email_invoice()
        moves = self.AccountMove.search(
            self.AccountMove._email_invoice_to_send_domain()
        )
        self.assertEqual(len(moves), 0)
        self.assertTrue(self.invoice.is_move_sent)

    def test_invoice_not_send_multiple_time(self):
        self.invoice.is_move_sent = True
        res = self.invoice._execute_invoice_sent_wizard()
        self.assertEqual(res, "This invoice has already been sent.")
