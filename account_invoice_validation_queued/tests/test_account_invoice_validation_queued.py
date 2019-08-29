# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import SavepointCase


class TestAccountInvoiceValidationQueued(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_obj = cls.env['account.invoice.confirm']
        cls.queue_obj = cls.env['queue.job']
        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'type': 'service',
        })
        cls.account_type = cls.env['account.account.type'].create({
            'name': 'Test account type',
        })
        cls.account = cls.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST_AIVQ',
            'user_type_id': cls.account_type.id,
        })
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'type': 'out_invoice',
            'account_id': cls.partner.property_account_receivable_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product.id,
                    'account_id': cls.account.id,
                    'price_unit': 20,
                    'quantity': 1,
                    'uom_id': cls.product.uom_id.id,
                }),
            ]
        })

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
        # Try to enqueue validation again
        with self.assertRaises(exceptions.UserError):
            wizard.enqueue_invoice_confirm()
        # Remove job
        self.invoice.validation_job_ids.cancel()
        self.assertFalse(self.invoice.validation_job_ids.exists())

    def test_queue_validation_several_dates(self):
        invoice2 = self.invoice.copy({'date_invoice': '2019-01-01'})
        wizard = self.wizard_obj.with_context(
            active_ids=(self.invoice + invoice2).ids,
        ).create({})
        with self.assertRaises(exceptions.UserError):
            wizard.enqueue_invoice_confirm()

    def test_validation(self):
        # Execute method directly for checking if validation is done
        self.invoice.action_invoice_open_job()
        self.assertEqual(self.invoice.state, 'open')
        wizard = self.wizard_obj.with_context(
            active_ids=self.invoice.ids,
        ).create({})
        # Try to enqueue validation against an already validated invoice
        with self.assertRaises(exceptions.UserError):
            wizard.enqueue_invoice_confirm()
