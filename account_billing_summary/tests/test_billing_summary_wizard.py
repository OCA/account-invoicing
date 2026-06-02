# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestBillingSummaryWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_model = cls.env["billing.summary.wizard"]
        cls.move_model = cls.env["account.move"]

        cls.account_revenue = cls.env["account.account"].search(
            [
                ("account_type", "=", "income"),
                ("company_ids", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.partner_a = cls.env["res.partner"].create(
            {"name": "Partner A", "ref": "CUST-001", "customer_rank": 1}
        )
        cls.partner_b = cls.env["res.partner"].create(
            {"name": "Partner B", "ref": "CUST-002", "customer_rank": 1}
        )
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Product Alpha", "type": "service"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Product Beta", "type": "service"}
        )
        cls.date_from = fields.Date.from_string("2026-01-01")
        cls.date_to = fields.Date.from_string("2026-01-31")

    def _create_invoice(
        self, partner, lines, move_type="out_invoice", date="2026-01-15"
    ):
        """Helper: create and post an invoice."""
        invoice = self.move_model.create(
            {
                "move_type": move_type,
                "partner_id": partner.id,
                "invoice_date": date,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "quantity": 1,
                            "price_unit": amount,
                            "account_id": self.account_revenue.id,
                        }
                    )
                    for product, amount in lines
                ],
            }
        )
        invoice.action_post()
        return invoice

    def _make_wizard(self, date_from=None, date_to=None, customers=None):
        return self.wizard_model.create(
            {
                "date_from": date_from or self.date_from,
                "date_to": date_to or self.date_to,
                "customer_ids": [Command.set(customers or [])],
                "company_ids": [Command.set([self.env.company.id])],
            }
        )

    # ── Tests ────────────────────────────────────────────────────────────────────

    def test_1_no_invoices_raises_user_error(self):
        """UserError when no posted invoices match the criteria."""
        wizard = self._make_wizard(
            date_from=fields.Date.from_string("2020-01-01"),
            date_to=fields.Date.from_string("2020-01-31"),
        )
        with self.assertRaises(UserError):
            wizard.action_export_excel()

    def test_2_get_invoices_respects_date_range(self):
        """Only invoices within date_from–date_to are returned."""
        self._create_invoice(self.partner_a, [(self.product_1, 100)], date="2026-01-15")
        self._create_invoice(self.partner_a, [(self.product_1, 200)], date="2026-02-01")

        wizard = self._make_wizard()
        invoices = wizard._get_invoices()
        dates = invoices.mapped("invoice_date")
        self.assertTrue(all(self.date_from <= d <= self.date_to for d in dates))

    def test_3_get_invoice_lines_returns_product_lines_only(self):
        """_get_invoice_lines returns only product display_type lines."""
        invoice = self._create_invoice(
            self.partner_a, [(self.product_1, 100), (self.product_2, 200)]
        )
        wizard = self._make_wizard()
        lines = wizard._get_invoice_lines(invoice)
        self.assertTrue(all(ln.display_type == "product" for ln in lines))
        self.assertTrue(all(ln.product_id for ln in lines))
        self.assertEqual(len(lines), 2)

    def test_4_get_products_returns_unique_sorted(self):
        """_get_products returns unique products sorted by name."""
        inv1 = self._create_invoice(self.partner_a, [(self.product_1, 100)])
        inv2 = self._create_invoice(
            self.partner_b, [(self.product_1, 50), (self.product_2, 75)]
        )
        wizard = self._make_wizard()
        lines = wizard._get_invoice_lines(inv1 | inv2)
        products = wizard._get_products(lines)
        self.assertEqual(len(products), 2)
        names = [p.name for p in products]
        self.assertEqual(names, sorted(names))

    def test_5_report_data_sums_multiple_invoices(self):
        """Amounts from multiple invoices for the same partner+product are summed."""
        self._create_invoice(self.partner_a, [(self.product_1, 100)])
        self._create_invoice(self.partner_a, [(self.product_1, 200)])
        wizard = self._make_wizard()
        invoices = wizard._get_invoices()
        lines = wizard._get_invoice_lines(invoices)
        report_data = wizard._get_report_data(lines)

        partner_row = next(
            r for r in report_data if r["partner"].id == self.partner_a.id
        )
        total = partner_row["amounts"].get(self.product_1.id, 0.0)
        self.assertAlmostEqual(total, 300.0)

    def test_6_report_data_subtracts_credit_notes(self):
        """Credit notes (out_refund) are subtracted from invoice totals."""
        self._create_invoice(self.partner_a, [(self.product_1, 500)])
        self._create_invoice(
            self.partner_a, [(self.product_1, 150)], move_type="out_refund"
        )
        wizard = self._make_wizard()
        invoices = wizard._get_invoices()
        lines = wizard._get_invoice_lines(invoices)
        report_data = wizard._get_report_data(lines)

        partner_row = next(
            r for r in report_data if r["partner"].id == self.partner_a.id
        )
        total = partner_row["amounts"].get(self.product_1.id, 0.0)
        self.assertAlmostEqual(total, 350.0)

    def test_7_filter_by_customer(self):
        """customer_ids filter limits invoices to selected partners."""
        self._create_invoice(self.partner_a, [(self.product_1, 100)])
        self._create_invoice(self.partner_b, [(self.product_2, 200)])
        wizard = self._make_wizard(customers=[self.partner_a.id])
        invoices = wizard._get_invoices()
        self.assertTrue(all(inv.partner_id == self.partner_a for inv in invoices))

    def test_8_action_export_excel_returns_act_url(self):
        """action_export_excel returns an ir.actions.act_url action."""
        self._create_invoice(self.partner_a, [(self.product_1, 100)])
        wizard = self._make_wizard()
        result = wizard.action_export_excel()
        self.assertEqual(result.get("type"), "ir.actions.act_url")
        self.assertIn(".xlsx", result.get("url", ""))
