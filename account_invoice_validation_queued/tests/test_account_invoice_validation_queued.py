# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.queue_job.job import Job


@tagged("post_install", "-at_install")
class TestAccountInvoiceValidationQueued(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.init_invoice("out_invoice", amounts=[20.0])

    def _enqueue(self, moves, **wizard_vals):
        wizard = (
            self.env["validate.account.move"]
            .with_context(active_model="account.move", active_ids=moves.ids)
            .create(wizard_vals)
        )
        wizard.enqueue_invoice_confirm()
        return wizard

    def _validation_jobs(self, move):
        return move.sudo().validation_job_ids

    def _perform_validation_jobs(self, move):
        for job in self._validation_jobs(move):
            Job.load(self.env, job.uuid).perform()

    def _create_future_invoice(self):
        return self.init_invoice(
            "out_invoice",
            invoice_date=fields.Date.today() + timedelta(days=10),
            amounts=[20.0],
        )

    def _bill_vals(self, price_unit):
        return {
            "move_type": "in_invoice",
            "partner_id": self.partner_a.id,
            "invoice_date": "2020-01-01",
            "line_ids": [
                Command.create(
                    {
                        "name": "product",
                        "price_unit": price_unit,
                        "tax_ids": [Command.clear()],
                    }
                )
            ],
        }

    def test_enqueued_job_posts_invoice(self):
        self._enqueue(self.invoice)
        jobs = self._validation_jobs(self.invoice)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(self.invoice.state, "draft")
        Job.load(self.env, jobs.uuid).perform()
        self.assertEqual(self.invoice.state, "posted")

    def test_posted_invoice_not_enqueued(self):
        posted_invoice = self.init_invoice("out_invoice", amounts=[10.0], post=True)
        self._enqueue(self.invoice | posted_invoice)
        self.assertEqual(len(self._validation_jobs(self.invoice)), 1)
        self.assertFalse(self._validation_jobs(posted_invoice))

    def test_enqueue_twice_single_job(self):
        self._enqueue(self.invoice)
        self._enqueue(self.invoice)
        self.assertEqual(len(self._validation_jobs(self.invoice)), 1)

    def test_future_invoice_waits_for_auto_post(self):
        invoice = self._create_future_invoice()
        self._enqueue(invoice)
        self._perform_validation_jobs(invoice)
        self.assertEqual(invoice.state, "draft")
        self.assertEqual(invoice.auto_post, "at_date")

    def test_force_post_posts_future_invoice(self):
        invoice = self._create_future_invoice()
        self._enqueue(invoice, force_post=True)
        self._perform_validation_jobs(invoice)
        self.assertEqual(invoice.state, "posted")

    def test_ignore_abnormal_amount(self):
        env = self.env(
            context=dict(self.env.context, disable_abnormal_invoice_detection=False)
        )
        AccountMove = env["account.move"]
        AccountMove.create([self._bill_vals(100) for __ in range(10)]).action_post()
        bill = AccountMove.create(self._bill_vals(200))
        wizard = self._enqueue(bill, ignore_abnormal_amount=True)
        self.assertEqual(wizard.abnormal_amount_partner_ids, self.partner_a)
        self.assertTrue(self.partner_a.ignore_abnormal_invoice_amount)
