# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import SavepointCase


class TestAccountInvoiceValidationQueued(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_obj = cls.env["validate.account.move"]
        cls.queue_obj = cls.env["queue.job"]

        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test account type", "internal_group": "equity"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST_AIVQ",
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
                            "price_unit": 20.0,
                            "quantity": 1.0,
                        },
                    ),
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

    def test_queue_validation_several_dates(self):
        invoice2 = self.invoice.copy({"date": "2019-01-01"})
        wizard = self.wizard_obj.with_context(
            active_ids=(self.invoice + invoice2).ids,
        ).create({})
        with self.assertRaises(exceptions.UserError):
            wizard.enqueue_invoice_confirm()

    def test_validation(self):
        # Execute method directly for checking if validation is done
        self.invoice.action_invoice_open_job()
        self.assertEqual(self.invoice.state, "posted")
