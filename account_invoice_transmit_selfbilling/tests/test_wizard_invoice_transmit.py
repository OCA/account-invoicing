# Copyright 2023 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.queue_job.tests.common import JobMixin, trap_jobs

from .common import SelfBillingTransmitCommon


class TestAccountInvoicePrintWizard(SelfBillingTransmitCommon, JobMixin):
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
        self.assertEqual(6, wizard.count_transmit_post)
        self.assertEqual(6, wizard.count_transmit_email)
        self.assertEqual(3, wizard.count_transmit_email_missing)
        self.assertEqual(3, wizard.count_transmit_undefined)

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
        self.assertAttachmentCount(self.invoices, 6)

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
            with trap_jobs() as trap_invidivual:
                trap.enqueued_jobs[0].perform()
                trap_invidivual.assert_jobs_count(3)
                trap_invidivual.enqueued_jobs[0].perform()
                trap_invidivual.enqueued_jobs[1].perform()
                trap_invidivual.enqueued_jobs[2].perform()
        mail_count_after = self.env["mail.mail"].search_count([]) - mail_count
        self.assertEqual(3, mail_count_after)
        # Mail template has attachment field value set
        self.assertAttachmentCount(self.invoices, 3)
