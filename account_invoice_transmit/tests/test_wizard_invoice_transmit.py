# Copyright 2023 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.queue_job.tests.common import JobMixin, trap_jobs

from .common import AccountInvoicePrintCommon


class TestAccountInvoicePrintWizard(AccountInvoicePrintCommon, JobMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["account.invoice.transmit"]

    def test_counters(self):
        """Test counters

        Data:
            partner_0 with transmit method "post"
            partner_1 with transmit method "mail"
            partner_2 with transmit method "post"
            partner_3 with transmit method "mail" without email
            partner_4 with no transmit method
        """
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})
        self.assertEqual(4, wizard.count_transmit_post)
        self.assertEqual(4, wizard.count_transmit_email)
        self.assertEqual(2, wizard.count_transmit_email_missing)
        self.assertEqual(2, wizard.count_transmit_undefined)

    def test_print(self):
        """Test print

        Data:
            partner_0 with 2 invoices and transmit method "post"
            partner_2 with 2 invoices and transmit method "post"
        Test case:
            Generate the all the invoices before launching the wizard
            Print all the invoices with the wizard
        Expected result:
            * 4 invoices are printed (partner_0 and partner_2) for sending
            method "post"
        """
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})

        with trap_jobs() as trap:
            wizard.button_print()
            trap.assert_jobs_count(1)
            trap.enqueued_jobs[0].perform()
        self.assertAttachmentCount(self.invoices, 4)

    def test_email(self):
        """Test email

        Data:
            partner_1 with 2 invoices and transmit method "mail"
        Test case:
            Generate the all the invoices before launching the wizard
            Generate the mail sending
        Expected result:
            * 2 invoices are in attachments
            * 2 mails are sent
        """
        mail_count = self.env["mail.mail"].search_count([])
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})

        with trap_jobs() as trap:
            wizard.button_email()
            trap.assert_jobs_count(1)
            trap.enqueued_jobs[0].perform()
        # Mail template has attachment field value set
        self.assertAttachmentCount(self.invoices, 2)
        mail_count_after = self.env["mail.mail"].search_count([]) - mail_count
        self.assertEqual(2, mail_count_after)

    def test_mark_as_sent(self):
        """Test mark as sent and resend

        Data:
            partner_0 with transmit method "post"
            partner_1 with transmit method "mail"
            partner_2 with transmit method "post"
            partner_3 with transmit method "mail" without email
        Test case:
            Generate the all the invoices before launching the wizard
            Mark them as sent
        Expected result:
            * Invoices should be marked as sent
            * No attachment should have been generated
        """
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})
        wizard.button_mark_only()
        self.assertTrue(all(invoice.is_move_sent for invoice in self.invoices))
        self.assertAttachmentCount(self.invoices, 0)

        # Check the counters
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})
        self.assertEqual(0, wizard.count_transmit_email)
        self.assertEqual(0, wizard.count_transmit_post)
        wizard.resend = True
        self.assertEqual(4, wizard.count_transmit_email)
        self.assertEqual(4, wizard.count_transmit_post)

    def test_related_post(self):
        """Test open invoices from job for post"""
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})

        invoices = wizard.transmit_post_invoice_ids
        self.assertEqual(4, len(invoices))
        counter = self.job_counter()
        wizard.button_print()
        job = counter.search_created()
        action = job.related_action_open_invoice()
        domain = action.get("domain")
        self.assertListEqual(invoices.ids, domain[0][2])

    def test_related_email(self):
        """Test open invoices from job for email"""
        wizard = self.Wizard.with_context(
            active_ids=self.invoices.ids, active_model="account.move"
        ).create({})

        invoices = wizard.transmit_email_valid_invoice_ids
        self.assertEqual(2, len(invoices))
        counter = self.job_counter()
        wizard.button_email()
        job = counter.search_created()
        action = job.related_action_open_invoice()
        domain = action.get("domain")
        self.assertListEqual(invoices.ids, domain[0][2])
