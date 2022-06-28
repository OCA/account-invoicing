# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountInvoiceMerge(TransactionCase):
    """
    Tests for Account Invoice Merge.
    """

    def setUp(self):
        super(TestAccountInvoiceMerge, self).setUp()
        self.company_model = self.env["res.company"]
        self.par_model = self.env["res.partner"]
        self.context = self.env["res.users"].context_get()
        self.acc_model = self.env["account.account"]
        self.inv_model = self.env["account.move"]
        self.journal_model = self.env["account.journal"]
        self.inv_line_model = self.env["account.move.line"]
        self.wiz = self.env["invoice.merge"]

        self.partner1 = self._create_partner()
        self.partner2 = self._create_partner()

        self.invoice_account = self.acc_model.search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )
        line_values = self._get_inv_line_values(self.invoice_account)

        self.invoice1 = self._create_invoice(self.partner1, "A", line_values)
        self.invoice2 = self._create_invoice(self.partner1, "B", line_values)
        self.invoice3 = self._create_invoice(self.partner2, "C", line_values)

    def _create_partner(self):
        partner = self.par_model.create(
            {
                "name": "Test Partner",
                "company_type": "company",
            }
        )
        return partner

    def _get_inv_line_values(self, account_id):
        line_values = [
            (
                0,
                0,
                {
                    "name": "test invoice line",
                    "account_id": account_id.id,
                    "quantity": 1.0,
                    "price_unit": 3.0,
                    "product_id": self.env.ref("product.product_product_8").id,
                },
            )
        ]
        return line_values

    def _create_invoice(
        self,
        partner,
        name,
        line_values,
        move_type="out_invoice",
        journal_type="sale",
        journal=False,
    ):
        journal = journal or self.journal_model.search(
            [("type", "=", journal_type)], limit=1
        )
        invoice = self.inv_model.with_company(journal.company_id).create(
            {
                "move_type": move_type,
                "partner_id": partner.id,
                "name": name,
                "invoice_line_ids": line_values,
                "journal_id": journal.id,
            }
        )
        return invoice

    def _get_wizard(self, active_ids, create=False):
        wiz_id = self.wiz.with_context(
            active_ids=active_ids,
            active_model="account.move",
        )
        if create:
            wiz_id = wiz_id.create({})
        return wiz_id

    def test_account_invoice_merge_1(self):
        self.assertEqual(len(self.invoice1.invoice_line_ids), 1)
        self.assertEqual(len(self.invoice2.invoice_line_ids), 1)
        start_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(start_inv), 2)

        wiz_id = self._get_wizard([self.invoice1.id, self.invoice2.id], create=True)
        wiz_id.fields_view_get()
        action = wiz_id.merge_invoices()

        self.assertLessEqual(
            {
                "type": "ir.actions.act_window",
                "binding_view_types": "list,form",
                "xml_id": "account.action_move_out_invoice_type",
            }.items(),
            action.items(),
            "There was an error and the two invoices were not merged.",
        )

        end_inv = self.inv_model.search(
            [("state", "=", "draft"), ("partner_id", "=", self.partner1.id)]
        )
        self.assertEqual(len(end_inv), 1)
        self.assertEqual(len(end_inv[0].invoice_line_ids), 1)
        self.assertEqual(end_inv[0].invoice_line_ids[0].quantity, 2.0)

    def test_account_invoice_merge_2(self):
        with self.assertRaises(UserError):
            self._get_wizard(
                [self.invoice1.id, self.invoice3.id], create=True
            ).fields_view_get()

    def test_dirty_check(self):
        """Check"""
        # Check with only one invoice
        with self.assertRaises(UserError):
            self._get_wizard([self.invoice1.id]).fields_view_get()

        # Check with two different invoice type
        # Create the invoice 4 with a different account
        new_account = self.acc_model.create(
            {
                "code": "TEST",
                "name": "Test Account",
                "reconcile": True,
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
            }
        )
        line_values = self._get_inv_line_values(new_account)
        invoice4 = self._create_invoice(
            self.partner1,
            "D",
            line_values,
            move_type="in_invoice",
            journal_type="purchase",
        )
        with self.assertRaises(UserError):
            self._get_wizard([self.invoice1.id, invoice4.id]).fields_view_get()

        # Check with a canceled invoice
        # Create and cancel the invoice 5
        line_values = self._get_inv_line_values(self.invoice_account)
        invoice5 = self._create_invoice(self.partner1, "E", line_values)
        invoice5.button_cancel()
        with self.assertRaises(UserError):
            self._get_wizard([self.invoice1.id, invoice5.id]).fields_view_get()

        # Check with another company
        # Create the invoice 6 in new company
        new_company = self.company_model.create({"name": "Hello World"})
        new_account = self.acc_model.create(
            {
                "name": "New Account",
                "code": "AAABBB",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
                "company_id": new_company.id,
            }
        )
        line_values = self._get_inv_line_values(new_account)
        new_journal = self.journal_model.create(
            {
                "name": "Test Journal",
                "company_id": new_company.id,
                "type": "sale",
                "code": "AAABBB",
            }
        )
        invoice6 = self._create_invoice(
            self.partner1, "E", line_values, journal=new_journal
        )
        with self.assertRaises(UserError):
            self._get_wizard([self.invoice1.id, invoice6.id]).fields_view_get()

        # Check with two different partners
        with self.assertRaises(UserError):
            self._get_wizard([self.invoice1.id, self.invoice3.id]).fields_view_get()
