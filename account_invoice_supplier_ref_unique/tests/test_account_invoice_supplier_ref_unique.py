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
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        # ENVIRONMENTS
        cls.account_account = cls.env["account.account"]
        cls.account_move = cls.env["account.move"].with_context(
            **{"tracking_disable": True}
        )

        # INSTANCES
        cls.partner = cls.env.ref("base.res_partner_2")
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

    def test_onchange_supplier_invoice_number(self):
        self.invoice._onchange_supplier_invoice_number()
        self.assertEqual(
            self.invoice.ref,
            self.invoice.supplier_invoice_number,
            "_onchange_supplier_invoice_number",
        )

    def test_copy_invoice(self):
        invoice2 = self.invoice.copy()
        self.assertNotEqual(self.invoice.ref, "")
        self.assertEqual(invoice2.ref, "")

    def test_reverse_invoice(self):
        self.invoice._post()
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=self.invoice.ids)
            .create(
                {
                    "date": fields.Date.today(),
                    "reason": "no reason",
                    "refund_method": "refund",
                    "journal_id": self.invoice.journal_id.id,
                }
            )
        )
        reversal = move_reversal.reverse_moves()
        refund = self.env["account.move"].browse(reversal["res_id"])
        self.assertNotEqual(self.invoice.ref, "")
        self.assertEqual(refund.ref, "")

    def test_reverse_moves_robustness(self):
        res = self.invoice._reverse_moves()
        self.assertTrue(res.is_purchase_document(include_receipts=True))

    def test_reverse_moves_keeps_context_supplier_ref(self):
        """Simulate the SII refund flow: l10n_es_aeat_sii_oca reads the
        supplier invoice number from context and sets it in ``default_values``
        before calling super(). That deliberately-set ``ref`` must survive
        instead of being blanked on the vendor credit note. Reproduced here
        without depending on l10n_es_aeat_sii_oca by injecting both the context
        key and the ref, exactly as that module does."""
        refund = self.invoice.with_context(
            supplier_invoice_number="REF-REFUND-001"
        )._reverse_moves([{"ref": "REF-REFUND-001"}])
        self.assertEqual(refund.ref, "REF-REFUND-001")

    def test_copy_keeps_context_supplier_ref(self):
        """copy() must keep a ref deliberately provided in context."""
        invoice2 = self.invoice.with_context(
            supplier_invoice_number="REF-COPY-001"
        ).copy({"ref": "REF-COPY-001"})
        self.assertEqual(invoice2.ref, "REF-COPY-001")

    def test_reverse_moves_batch_only_matching_move_keeps_ref(self):
        """The guard is per move: in a mixed batch only the move whose ref
        matches the context-provided supplier invoice number keeps it; an
        unrelated move reverted in the same batch is still blanked."""
        invoice2 = self.account_move.create(
            {
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today(),
                "move_type": "in_invoice",
                "supplier_invoice_number": "DEF456",
                "invoice_line_ids": [(0, 0, {"partner_id": self.partner.id})],
            }
        )
        moves = self.invoice + invoice2
        refunds = moves.with_context(
            supplier_invoice_number="REF-REFUND-001"
        )._reverse_moves([{"ref": "REF-REFUND-001"}, {"ref": "Reversal of: BILL"}])
        by_source = {r.reversed_entry_id.id: r for r in refunds}
        self.assertEqual(by_source[self.invoice.id].ref, "REF-REFUND-001")
        self.assertEqual(by_source[invoice2.id].ref, "")
