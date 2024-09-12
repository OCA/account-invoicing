# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from unittest import mock
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountInvoiceMerge(TransactionCase):
    """
    Tests for Account Invoice Merge.
    """

    def setUp(self):
        super().setUp()
        self.par_model = self.env["res.partner"]
        self.context = self.env["res.users"].context_get()
        self.acc_model = self.env["account.account"]
        self.inv_model = self.env["account.move"]
        self.inv_line_model = self.env["account.move.line"]
        self.wiz = self.env["invoice.merge"]
        self.product = self.env.ref("product.product_product_8")
        self.account_receive = self.env.ref("account.data_account_type_receivable")
        self.partner1 = self._create_partner()
        self.partner2 = self._create_partner()
        self.invoice_account = self.acc_model.search(
            [("user_type_id", "=", self.account_receive.id)],
            limit=1,
        )
        self.journal = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        self.invoice1 = self._create_invoice(self.partner1, "A")
        self.invoice2 = self._create_invoice(self.partner1, "B")
        self.invoice3 = self._create_invoice(self.partner2, "C")

        self.invoice_line1 = self._create_inv_line(self.invoice1)
        self.invoice_line2 = self._create_inv_line(self.invoice2)
        self.invoice_line3 = self._create_inv_line(self.invoice3)
        self.user2 = self.env["res.users"].create(
            {
                "login": "test2",
                "name": "test2",
            }
        )

    def _create_partner(self):
        partner = self.par_model.create(
            {"name": "Test Partner", "supplier_rank": 1, "company_type": "company"}
        )
        return partner

    def _create_inv_line(self, invoice):
        lines = invoice.invoice_line_ids
        invoice.write(
            {
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "name": "test invoice line",
                            "quantity": 1.0,
                            "price_unit": 3.0,
                            "move_id": invoice.id,
                            "product_id": self.product.id,
                            "exclude_from_invoice_tab": False,
                        },
                    )
                ]
            }
        )
        return invoice.invoice_line_ids - lines

    def _create_invoice(self, partner, name, journal=False, move_type=False):
        if not journal:
            journal = self.journal
        if not move_type:
            move_type = "out_invoice"
        invoice = self.inv_model.create(
            {
                "partner_id": partner.id,
                "name": name,
                "move_type": move_type,
                "journal_id": journal.id,
            }
        )
        return invoice

    def test_account_invoice_merge_1(self):
        self.assertEqual(len(self.invoice1.invoice_line_ids), 1)
        self.assertEqual(len(self.invoice2.invoice_line_ids), 1)
        start_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(start_inv), 2)
        invoices = self.invoice1 | self.invoice2
        wiz_id = self.wiz.with_context(
            active_ids=invoices.ids,
            active_model=invoices._name,
        ).create({})
        wiz_id.fields_view_get()
        action = wiz_id.merge_invoices()

        self.assertEqual(
            action["type"],
            "ir.actions.act_window",
            "There was an error and the two invoices were not merged.",
        )
        self.assertEqual(
            action["xml_id"],
            "account.action_move_out_invoice_type",
            "There was an error and the two invoices were not merged.",
        )

        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(end_inv), 1)
        self.assertEqual(len(end_inv[0].invoice_line_ids), 1)
        self.assertEqual(end_inv[0].invoice_line_ids[0].quantity, 2.0)
        self.assertEqual(end_inv.name, "/")

    def test_account_invoice_merge_2(self):
        invoices = self.invoice1 | self.invoice3
        wiz_id = self.wiz.with_context(
            active_ids=invoices.ids,
            active_model=invoices._name,
        ).create({})
        with self.assertRaises(UserError):
            wiz_id.fields_view_get()

    def test_dirty_check(self):
        """Check"""
        wiz_id = self.wiz.with_context(active_model="account.move")

        # Check with only one invoice
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=self.invoice1.ids, active_model=self.invoice1._name
            ).fields_view_get()

        # Check with two different invoice type
        # Create the invoice 4 with a different account
        invoice4 = self._create_invoice(self.partner1, "D")
        invoice4.write({"move_type": "out_refund"})
        self._create_inv_line(invoice4)
        invoices = self.invoice1 | invoice4
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=invoices.ids,
                active_model=invoices._name,
            ).fields_view_get()

        # Check with a canceled invoice
        # Create and cancel the invoice 5
        invoice5 = self._create_invoice(self.partner1, "E")
        self._create_inv_line(invoice5)
        invoice5.button_cancel()
        invoices = self.invoice1 | invoice5
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=invoices.ids,
                active_model=invoices._name,
            ).fields_view_get()

        # Check with an another company
        # Create the invoice 6 and change the company
        new_company = self.env["res.company"].create({"name": "Hello World"})
        new_journal = self.journal.with_company(new_company).copy()
        invoice6 = self._create_invoice(self.partner1, "E", new_journal)
        self._create_inv_line(invoice6)
        invoices = self.invoice1 | invoice6
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=invoices.ids,
                active_model=invoices._name,
            ).fields_view_get()

        # Check with two different partners
        invoices = self.invoice1 | self.invoice3
        with self.assertRaises(UserError):
            wiz_id.with_context(
                active_ids=invoices.ids,
                active_model=invoices._name,
            ).fields_view_get()

    def test_account_invoice_merge_3(self):

        expenses_journal = self.env["account.journal"].create(
            {
                "name": "Vendor Bills - Test",
                "code": "TEXJ",
                "type": "purchase",
                "refund_sequence": True,
            }
        )
        inv_a = self._create_invoice(
            self.partner1, "A", journal=expenses_journal, move_type="in_invoice"
        )
        inv_b = self._create_invoice(
            self.partner1, "A", journal=expenses_journal, move_type="in_invoice"
        )
        inv_b.write({"user_id": self.user2.id})
        self.assertNotEqual(inv_a.user_id, inv_b.user_id)
        invoices = inv_a | inv_b
        wiz_id = self.wiz.with_context(
            active_ids=invoices.ids,
            active_model=invoices._name,
        ).create({})
        wiz_id.fields_view_get()
        wiz_id.merge_invoices()

    @mock.patch(
        "odoo.addons.account_invoice_merge.models.account_move.AccountMove.post_merge_message"
    )
    @mock.patch(
        "odoo.addons.account_invoice_merge.models.account_move.AccountMove.post_process_fields"
    )
    def test_account_invoice_merge_4(
        self, mock_post_process_fields, mock_post_merge_message
    ):
        invoices = self.invoice1 | self.invoice2
        wiz_id = self.wiz.with_context(
            active_ids=invoices.ids,
            active_model=invoices._name,
        ).create({})
        wiz_id.fields_view_get()
        wiz_id.merge_invoices()
        mock_post_process_fields.assert_called_once_with(invoices)
        mock_post_merge_message.assert_called_once_with(invoices)

    def test_get_post_merge_message_invoice_identifier(self):
        """Test that the post-merge message invoice identifier is correct."""
        self.assertEqual(
            self.invoice1._get_post_merge_message_invoice_identifier(),
            f"account.move({self.invoice1.id})",
        )

    def test_post_merge_message(self):
        """Test that the post-merge message is displayed when merging invoices."""
        invoices = self.invoice1 | self.invoice2
        invoice_3 = self._create_invoice(self.partner1, "C")
        message_li_invoice_1 = (
            f'<li><a href="/web#id={self.invoice1.id}'
            f'&model=account.move&view_type=form" >'
            f"{self.invoice1._get_post_merge_message_invoice_identifier()}"
            f" - "
            f"{self.invoice1.amount_total}</a></li>"
        )

        message_li_invoice_2 = (
            f'<li><a href="/web#id={self.invoice2.id}'
            f'&model=account.move&view_type=form" >'
            f"{self.invoice2._get_post_merge_message_invoice_identifier()}"
            f" - "
            f"{self.invoice2.amount_total}</a></li>"
        )
        message_body = (
            f"Invoice merged from :"
            f"<ul>{message_li_invoice_1}{message_li_invoice_2}</ul>"
        )
        with patch(
            "odoo.addons.mail.models.mail_thread.MailThread.message_post"
        ) as mock_message_post:
            invoice_3.post_merge_message(invoices)
            self.assertEqual(mock_message_post.call_count, 1)
            self.assertEqual(mock_message_post.call_args[1].get("body"), message_body)

    @patch(
        (
            "odoo.addons.account_invoice_merge.models.account_move.AccountMove."
            "_get_fields_to_concatenate_after_merge"
        ),
        return_value=["ref"],
    )
    def test_post_process_fields(self, mock_get_fields_to_concatenate_after_merge):
        self.invoice1.ref = "Blabla1"
        self.invoice2.ref = "Blabla2"
        invoices = self.invoice1 | self.invoice2
        invoice_3 = self._create_invoice(self.partner1, "C")
        invoice_3.post_process_fields(invoices)
        self.assertEqual(invoice_3.ref, "Blabla1 // Blabla2")
