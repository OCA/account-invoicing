# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase

from ..models.account_move import GROUP_AICT, GROUP_AICT_ADJUST


class TestAccountInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_move = cls.env["account.move"]

        cls.group_check_total = cls.env.ref(GROUP_AICT)
        cls.group_adjust_total = cls.env.ref(GROUP_AICT_ADJUST)
        cls.group_check_total.write({"users": [(4, cls.env.user.id)]})

        cls.partner = cls.env["res.partner"].create({"name": "test partner"})
        cls.adjustment_account = cls.env["account.account"].create(
            {
                "name": "Supplier Invoice Adjustment",
                "code": "XAITEST",
                "account_type": "expense",
                "company_id": cls.env.company.id,
            }
        )
        cls.purchase_journal = cls.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )
        cls.purchase_journal.supplier_inv_adjustment_account_id = cls.adjustment_account

    def _create_vendor_bill(
        self,
        check_total=1.19,
        price_unit=2.99,
        journal=None,
    ):
        invoice_form = Form(
            self.account_move.with_context(default_move_type="in_invoice")
        )
        invoice_form.partner_id = self.partner
        invoice_form.check_total = check_total
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "Test invoice line"
            line_form.price_unit = price_unit
            line_form.tax_ids.clear()
        invoice = invoice_form.save()
        invoice.journal_id = journal or self.purchase_journal
        return invoice

    def test_post(self):
        invoice = self._create_vendor_bill()
        self.assertAlmostEqual(invoice.check_total, 1.19)
        self.assertAlmostEqual(invoice.check_total_display_difference, -1.80)
        with self.assertRaises(ValidationError):
            invoice.action_post()

    def test_action_create_check_total_adjustment_line(self):
        self.group_adjust_total.write({"users": [(4, self.env.user.id)]})
        invoice = self._create_vendor_bill()
        self.assertAlmostEqual(invoice.amount_total, 2.99)
        self.assertAlmostEqual(invoice.check_total, 1.19)
        self.assertAlmostEqual(invoice.check_total_display_difference, -1.8)
        lines = invoice.invoice_line_ids
        self.assertEqual(len(lines), 1)
        invoice.action_create_check_total_adjustment_line()
        self.assertEqual(len(invoice.invoice_line_ids), 2)
        adjustment_line = invoice.invoice_line_ids - lines
        self.assertEqual(adjustment_line.account_id, self.adjustment_account)
        self.assertEqual(adjustment_line.quantity, 1.0)
        self.assertAlmostEqual(adjustment_line.price_unit, -1.80)
        self.assertAlmostEqual(adjustment_line.price_subtotal, -1.80)
        invoice._compute_amount()
        self.assertAlmostEqual(invoice.amount_total, 1.19)
        self.assertAlmostEqual(invoice.check_total_display_difference, 0.0)

    def test_action_create_check_total_adjustment_line_without_group(self):
        invoice = self._create_vendor_bill()
        with self.assertRaisesRegex(
            ValidationError, "You are not allowed to create an adjustment line"
        ):
            invoice.action_create_check_total_adjustment_line()

    def test_action_create_check_total_adjustment_line_without_account(self):
        self.group_adjust_total.write({"users": [(4, self.env.user.id)]})
        journal = self.purchase_journal.copy(
            {
                "name": "Purchase Journal Test No Adjust",
                "code": "PJNA",
                "supplier_inv_adjustment_account_id": False,
            }
        )
        invoice = self._create_vendor_bill(journal=journal)
        with self.assertRaisesRegex(
            ValidationError,
            "Please configure a Supplier Invoice Adjustment Account on the journal",
        ):
            invoice.action_create_check_total_adjustment_line()
