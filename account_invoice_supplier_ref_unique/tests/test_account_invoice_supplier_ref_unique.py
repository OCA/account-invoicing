# Copyright 2016 Acsone
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceSupplierRefUnique(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # ENVIRONMENTS
        cls.account_account = cls.env["account.account"]
        cls.account_move = cls.env["account.move"].with_context(
            **{"tracking_disable": True}
        )

        # INSTANCES
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        # Account for invoice
        cls.account = cls.account_account.search(
            [
                (
                    "account_type",
                    "=",
                    "asset_receivable",
                )
            ],
            limit=1,
        )
        # Invoice with unique reference 'ABC123'
        cls.invoice = cls.account_move.create(
            {
                "partner_id": cls.partner.id,
                "invoice_date": fields.Date.today(),
                "move_type": "in_invoice",
                "supplier_invoice_number": "ABC123",
                "invoice_line_ids": [(0, 0, {"partner_id": cls.partner.id})],
            }
        )

        # Activate unique number check
        cls.env.company.check_invoice_supplier_number = True

    def test_check_unique_supplier_invoice_number_insensitive(self):
        # A new invoice instance with an existing supplier_invoice_number
        with self.assertRaises(ValidationError):
            self.account_move.create(
                {
                    "partner_id": self.partner.id,
                    "move_type": "in_invoice",
                    "supplier_invoice_number": "ABC123",
                }
            )
        # A new invoice instance with a new supplier_invoice_number
        self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "supplier_invoice_number": "ABC123bis",
            }
        )

    def test_no_check_unique_supplier_invoice_number(self):
        # A new invoice instance with an existing supplier_invoice_number
        self.env.company.check_invoice_supplier_number = False
        self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "supplier_invoice_number": "ABC123",
            }
        )

    def test_check_empty_supplier_invoice_number(self):
        # When supplier_invoice_number is empty, validation should pass
        invoice = self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "supplier_invoice_number": "",
                "invoice_line_ids": [(0, 0, {"partner_id": self.partner.id})],
            }
        )
        # Should not raise an error when supplier_invoice_number is empty
        self.assertEqual(invoice.supplier_invoice_number, "")

    def test_onchange_supplier_invoice_number(self):
        self.invoice._onchange_supplier_invoice_number()
        self.assertEqual(
            self.invoice.ref,
            self.invoice.supplier_invoice_number,
            "_onchange_supplier_invoice_number",
        )

    def test_onchange_supplier_invoice_number_preserves_existing_ref(self):
        # When ref already exists, it should not be overwritten
        invoice = self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "ref": "EXISTING-REF",
                "supplier_invoice_number": "NEW-NUMBER",
                "invoice_line_ids": [(0, 0, {"partner_id": self.partner.id})],
            }
        )
        invoice._onchange_supplier_invoice_number()
        self.assertEqual(invoice.ref, "EXISTING-REF")

    def test_copy_invoice(self):
        invoice2 = self.invoice.copy()
        self.assertNotEqual(self.invoice.ref, "")
        self.assertEqual(invoice2.ref, "")

    def test_copy_customer_invoice_keeps_ref(self):
        customer_invoice = self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "ref": "CUST-001",
                "invoice_line_ids": [(0, 0, {"partner_id": self.partner.id})],
            }
        )

        customer_invoice2 = customer_invoice.copy()

        self.assertEqual(customer_invoice.ref, "CUST-001")
        self.assertEqual(customer_invoice2.ref, "CUST-001")

    def test_copy_customer_invoice_without_ref(self):
        customer_invoice = self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [(0, 0, {"partner_id": self.partner.id})],
            }
        )

        customer_invoice2 = customer_invoice.copy()

        self.assertFalse(customer_invoice.ref)
        self.assertFalse(customer_invoice2.ref)

    def test_reverse_invoice(self):
        self.invoice._post()
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=self.invoice.ids)
            .create(
                {
                    "date": fields.Date.today(),
                    "reason": "no reason",
                    "journal_id": self.invoice.journal_id.id,
                }
            )
        )
        reversal = move_reversal.reverse_moves()
        refund = self.env["account.move"].browse(reversal["res_id"])
        self.assertNotEqual(self.invoice.ref, "")
        self.assertEqual(refund.ref, "")

    def test_reverse_moves_keeps_empty_ref_in_defaults(self):
        default_values_list = [{"ref": ""}]

        self.invoice._reverse_moves(default_values_list=default_values_list)

        self.assertEqual(default_values_list[0]["ref"], "")
        self.assertIn("ref", default_values_list[0])

    def test_reverse_moves_clears_ref_for_purchase_document(self):
        # Ensure the update({"ref": ""}) branch is covered: a purchase document
        # with a non-empty ref in default_values should have it cleared in the
        # reversal, without mutating the original list.
        self.invoice._post()
        default_values_list = [{"ref": "REVERSAL-REF"}]

        reversed_moves = self.invoice._reverse_moves(
            default_values_list=default_values_list
        )

        self.assertEqual(default_values_list[0]["ref"], "REVERSAL-REF")
        self.assertEqual(reversed_moves.ref, "")

    def test_reverse_moves_robustness(self):
        res = self.invoice._reverse_moves()
        self.assertTrue(res.is_purchase_document(include_receipts=True))

    def test_reverse_moves_with_multiple_default_values(self):
        # Test _reverse_moves with multiple default values entries
        default_values_list = [{"ref": "REVERSAL-REF-1"}, {"ref": ""}]
        reversed_moves = self.invoice._reverse_moves(
            default_values_list=default_values_list
        )
        # The first default_values should be cleared since it's a purchase document
        self.assertEqual(default_values_list[0]["ref"], "REVERSAL-REF-1")
        # Result should have empty ref
        self.assertEqual(reversed_moves.ref, "")

    def test_reverse_moves_for_sale_document(self):
        # For sales documents, the override must not clear ref in defaults.
        customer_invoice = self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "ref": "SALES-001",
                "invoice_line_ids": [(0, 0, {"partner_id": self.partner.id})],
            }
        )
        customer_invoice._post()
        default_values_list = [{"ref": "SALES-REF"}]

        reversed_moves = customer_invoice._reverse_moves(
            default_values_list=default_values_list
        )

        self.assertEqual(default_values_list[0]["ref"], "SALES-REF")
        self.assertEqual(reversed_moves.ref, "SALES-001")
