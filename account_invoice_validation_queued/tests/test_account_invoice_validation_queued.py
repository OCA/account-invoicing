# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import TransactionCase


class TestAccountInvoiceValidationQueued(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_obj = cls.env["validate.account.move"]
        cls.queue_obj = cls.env["queue.job"]

        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST.AIVQ",
                "account_type": "equity",
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Test product",
                            "account_id": cls.account.id,
                            "price_unit": 20.0,
                            "quantity": 1.0,
                        }
                    )
                ],
            }
        )

    def test_queue_validation(self):
        wizard = self.wizard_obj.with_context(
            active_ids=self.invoice.ids,
        ).create({})
        prev_jobs = self.queue_obj.search([])
        wizard.enqueue_invoice_confirm()
        current_jobs = self.queue_obj.search([])
        jobs = current_jobs - prev_jobs
        self.assertEqual(len(jobs), 1)
        self.assertTrue(self.invoice.validation_job_ids)

    def test_validation(self):
        # Execute method directly for checking if validation is done
        self.invoice.action_invoice_open_job()
        self.assertEqual(self.invoice.state, "posted")
