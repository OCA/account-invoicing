# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestAccountInvoiceSendQueued(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_obj = cls.env["account.invoice.send"]
        cls.queue_obj = cls.env["queue.job"]

        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test account type", "internal_group": "equity"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST_AISQ",
                "user_type_id": cls.account_type.id,
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test product",
                            "account_id": cls.account.id,
                            "price_unit": 100.0,
                            "quantity": 1.0,
                        },
                    ),
                ],
            }
        )

    def test_queue_email_send(self):
        wizard = self.wizard_obj.with_context(
            active_ids=self.invoice.ids,
        ).create({})
        prev_jobs = self.queue_obj.search([])
        wizard.enqueue_invoice_email_send()
        current_jobs = self.queue_obj.search([])
        jobs = current_jobs - prev_jobs
        self.assertEqual(len(jobs), 1)
        self.assertTrue(self.invoice.email_send_job_ids)

    def test_email_send(self):
        # Execute method directly like as a job
        self.invoice.action_invoice_send_email_job()
        self.assertTrue(self.invoice.is_move_sent)
