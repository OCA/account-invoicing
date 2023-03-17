# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import exceptions
from odoo.tests import SavepointCase

from odoo.addons.queue_job.tests.common import trap_jobs


class TestAccountInvoiceMassSending(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice_obj = cls.env["account.move"]

        cls.partner1 = cls.env["res.partner"].create({"name": "Test partner 1"})
        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Test partner 2",
                "email": "test@mail.com",
            }
        )

        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test account type", "internal_group": "equity"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST_AIMS",
                "user_type_id": cls.account_type.id,
            }
        )
        cls.invoice1 = cls.invoice_obj.create(
            {
                "partner_id": cls.partner1.id,
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
        cls.invoice2 = cls.invoice_obj.create(
            {
                "partner_id": cls.partner2.id,
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
        cls.invoice3 = cls.invoice_obj.create(
            {
                "partner_id": cls.partner2.id,
                "move_type": "out_invoice",
                "sending_in_progress": True,
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
        cls.invoices = cls.invoice1 + cls.invoice2 + cls.invoice3

    def test_invoice_mass_sending_1(self):
        # test one invoice to send and no invoice in progress
        with trap_jobs() as trap:
            self.invoice2.mass_send_print()
            trap.assert_jobs_count(1, only=self.invoice_obj.do_prepare_send_print)

    def test_invoice_mass_sending_2(self):
        # test no invoice to send and one invoice in progress
        with trap_jobs() as trap:
            self.invoice3.mass_send_print()
            trap.assert_jobs_count(0, only=self.invoice_obj.do_prepare_send_print)

    def test_invoice_mass_sending_3(self):
        # test 2 invoice to send and 1 already in progress
        self.invoices = self.invoice1 | self.invoice2 | self.invoice3
        with trap_jobs() as trap:
            self.invoices.mass_send_print()
            self.assertTrue(all(self.invoices.mapped("sending_in_progress")))
            trap.assert_jobs_count(1, only=self.invoice_obj.do_prepare_send_print)
            trap.perform_enqueued_jobs()
            trap.assert_jobs_count(2, only=self.invoice_obj.do_send_print)

    def test_do_send_print(self):
        # partner of invoice1 has no email
        with self.assertRaises(exceptions.UserError):
            self.invoice1.do_send_print()
        self.invoice3.do_send_print()
        self.assertFalse(self.invoice3.sending_in_progress)
