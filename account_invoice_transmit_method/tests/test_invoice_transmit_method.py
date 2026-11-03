# Copyright 2017-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author: Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceTransmitMethod(BaseCommon):
    _test_user_groups = ("account.group_account_manager", "base.group_partner_manager")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mail_method = cls.env.ref("account_invoice_transmit_method.mail")
        cls.post_method = cls.env.ref("account_invoice_transmit_method.post")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Old School Company",
                "is_company": True,
                "customer_invoice_transmit_method_id": cls.post_method.id,
            }
        )
        cls.sale_journal = cls.env["account.journal"].create(
            {"code": "XYZZZ", "name": "sale journal (test)", "type": "sale"}
        )
        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "Vendor",
                "supplier_invoice_transmit_method_id": cls.post_method.id,
            }
        )
        cls.purchase_journal = cls.env["account.journal"].create(
            {"code": "VEN", "name": "vendor journal", "type": "purchase"}
        )

    def _create_move(self, move_type, partner, journal):
        return self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": partner.id,
                "journal_id": journal.id,
            }
        )

    def test_create_invoice(self):
        invoice = self._create_move("out_invoice", self.partner, self.sale_journal)
        self.assertEqual(invoice.transmit_method_id, self.post_method)
        self.assertEqual(invoice.transmit_method_code, "post")

    def test_create_customer_refund(self):
        refund = self._create_move("out_refund", self.partner, self.sale_journal)
        self.assertEqual(refund.transmit_method_id, self.post_method)

    def test_create_vendor_bill(self):
        bill = self._create_move("in_invoice", self.vendor, self.purchase_journal)
        self.assertEqual(bill.transmit_method_id, self.post_method)

    def test_create_vendor_refund(self):
        refund = self._create_move("in_refund", self.vendor, self.purchase_journal)
        self.assertEqual(refund.transmit_method_id, self.post_method)

    def test_customer_method_ignored_on_vendor_bill(self):
        bill = self._create_move("in_invoice", self.partner, self.purchase_journal)
        self.assertFalse(bill.transmit_method_id)

    def test_transmit_method_no_partner(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": False,
                "journal_id": self.sale_journal.id,
            }
        )
        self.assertFalse(invoice.transmit_method_id)

    def test_change_partner_recomputes_method(self):
        other = self.env["res.partner"].create(
            {
                "name": "Modern Company",
                "customer_invoice_transmit_method_id": self.mail_method.id,
            }
        )
        invoice = self._create_move("out_invoice", self.partner, self.sale_journal)
        invoice.partner_id = other
        self.assertEqual(invoice.transmit_method_id, self.mail_method)

    def test_manual_method_on_invoice(self):
        invoice = self._create_move("out_invoice", self.partner, self.sale_journal)
        invoice.transmit_method_id = self.mail_method
        self.assertEqual(invoice.transmit_method_id, self.mail_method)
        self.assertEqual(
            self.partner.customer_invoice_transmit_method_id, self.post_method
        )

    def test_commercial_fields_sync_to_contacts(self):
        contact = self.env["res.partner"].create(
            {"name": "Accountant", "parent_id": self.partner.id, "type": "invoice"}
        )
        self.assertEqual(contact.customer_invoice_transmit_method_id, self.post_method)
        self.partner.customer_invoice_transmit_method_id = self.mail_method
        self.assertEqual(contact.customer_invoice_transmit_method_id, self.mail_method)
        invoice = self._create_move("out_invoice", contact, self.sale_journal)
        self.assertEqual(invoice.transmit_method_id, self.mail_method)

    def test_invoice_contact_email_required_for_mail_method(self):
        self.partner.customer_invoice_transmit_method_id = self.mail_method
        partner_form = Form(self.partner)
        with partner_form.child_ids.new() as contact:
            contact.type = "invoice"
            contact.name = "Billing"
            with self.assertRaises(AssertionError):
                contact.save()
            contact.email = "billing@example.com"
        partner_form.save()
        self.assertEqual(self.partner.child_ids.email, "billing@example.com")

    def test_send_buttons_keep_core_condition(self):
        arch = etree.fromstring(
            self.env["account.move"].get_view(view_type="form")["arch"]
        )
        buttons = arch.xpath("//button[@name='action_invoice_sent']")
        self.assertEqual(len(buttons), 2)
        for button in buttons:
            invisible = button.get("invisible")
            self.assertIn("not display_send_button", invisible)
            self.assertTrue(
                invisible.endswith("or (transmit_method_code not in ('mail', False))")
            )
