# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import TransactionCase
from odoo.tests.common import Form


class TestAccountMove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("account.group_account_invoice")
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env.ref("product.product_product_3")

    def _create_invoice(self, **kwargs):
        invoice_vals = [
            Command.create(
                {
                    "product_id": self.product.id,
                    "quantity": 1.0,
                    "name": "Line 1",
                    "price_unit": 200.00,
                    **kwargs,
                },
            )
        ]
        invoice = (
            self.env["account.move"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "journal_id": (
                        self.env["account.journal"]
                        .search([("type", "=", "sale")], limit=1)
                        .id
                    ),
                    "partner_id": self.partner.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": invoice_vals,
                }
            )
        )
        return invoice

    def test_01_show_discount_warning_label(self):
        invoice = self._create_invoice(discount_fixed=10.00, discount1=10.00)
        self.assertTrue(invoice.show_discount_warning_label)
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line:
                line.discount_fixed = 0.0
        self.assertFalse(invoice.show_discount_warning_label)

    def test_02_get_lines_to_compute_discount(self):
        invoice = self._create_invoice(discount1=10.00, discount2=10.00)
        self.assertAlmostEqual(invoice.invoice_line_ids[0].discount, 19)
        lines = invoice.invoice_line_ids._get_lines_to_compute_discount()
        self.assertEqual(lines, invoice.invoice_line_ids)
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line:
                line.discount_fixed = 10.0
        lines = invoice.invoice_line_ids._get_lines_to_compute_discount()
        self.assertEqual(lines, invoice.invoice_line_ids - invoice.invoice_line_ids[0])

    def test_03_should_copy_discount_to_discount1(self):
        invoice = self._create_invoice(discount=10.00)
        self.assertAlmostEqual(invoice.invoice_line_ids[0].discount, 10)
        self.assertAlmostEqual(invoice.invoice_line_ids[0].discount1, 10)
        self.assertAlmostEqual(invoice.invoice_line_ids[0].discount_fixed, 0)
        invoice_2 = self._create_invoice(discount=10.00, discount_fixed=10.00)
        self.assertAlmostEqual(invoice_2.invoice_line_ids[0].discount, 5)  # 10€ of 200€
        self.assertAlmostEqual(invoice_2.invoice_line_ids[0].discount1, 0)
        self.assertAlmostEqual(invoice_2.invoice_line_ids[0].discount_fixed, 10)
