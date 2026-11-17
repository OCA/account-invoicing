# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from lxml import html

from odoo import Command

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestAccountMoveLineProductNameVisibility(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_1 = cls.env.company
        company_2_data = cls.setup_other_company()
        cls.company_2 = company_2_data["company"]
        cls.product = cls.product_a
        cls.product.write(
            {
                "name": "Test Desk Visibility",
                "default_code": False,
            }
        )
        cls.description = "Custom desk description"
        cls.invoice = (
            cls.env["account.move"]
            .with_company(cls.company_1)
            .create(
                {
                    "move_type": "out_invoice",
                    "partner_id": cls.partner_a.id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "product_id": cls.product.id,
                                "name": cls.description,
                                "quantity": 1.0,
                                "price_unit": 100.0,
                            }
                        ),
                    ],
                }
            )
        )
        cls.line = cls.invoice.invoice_line_ids.filtered(
            lambda line: line.product_id == cls.product
        )

    def _get_report_description(self, invoice):
        report = self.env.ref("account.account_invoices")
        content, _ = report._render_qweb_html(report.report_name, invoice.ids)
        document = html.fromstring(content)
        return " ".join(
            document.xpath("//td[@name='account_invoice_line_name']//text()")
        )

    def test_product_name_visibility(self):
        self.assertEqual(self.line.name, self.description)
        report_description = self._get_report_description(self.invoice)
        self.assertIn(self.product.name, report_description)
        self.assertIn(self.description, report_description)
        self.line.hide_product_name = True
        self.assertTrue(self.line.hide_product_name)
        report_description = self._get_report_description(self.invoice)
        self.assertNotIn(self.product.name, report_description)
        self.assertIn(self.description, report_description)
        second_line = self.env["account.move.line"].create(
            {
                "move_id": self.invoice.id,
                "product_id": self.product.id,
                "name": "Second desk description",
                "quantity": 1.0,
                "price_unit": 100.0,
            }
        )
        self.line.hide_product_name = True
        self.assertTrue(self.line.hide_product_name)
        self.assertFalse(second_line.hide_product_name)

    def test_product_template_hide_product_name(self):
        self.product.hide_product_name = True
        self.assertTrue(self.line.hide_product_name)
        self.assertTrue(self.product.hide_product_name)
        report_description = self._get_report_description(self.invoice)
        self.assertNotIn(self.product.name, report_description)
        self.assertIn(self.description, report_description)

    def test_company_default_hide_product_name(self):
        self.company_1.hide_product_name = True
        # Does not affect existing invoices
        report_description = self._get_report_description(self.invoice)
        self.assertIn(self.product.name, report_description)
        invoice = (
            self.env["account.move"]
            .with_company(self.company_1)
            .create(
                {
                    "move_type": "in_invoice",
                    "partner_id": self.partner_a.id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "product_id": self.product.id,
                                "name": self.description,
                                "quantity": 1.0,
                                "price_unit": 100.0,
                            }
                        ),
                    ],
                }
            )
        )
        self.assertTrue(invoice.invoice_line_ids.hide_product_name)
        report_description = self._get_report_description(invoice)
        self.assertNotIn(self.product.name, report_description)
        self.assertIn(self.description, report_description)

    def test_multicompany_hide_product_name(self):
        self.product.with_company(self.company_1).hide_product_name = True
        self.assertTrue(self.product.with_company(self.company_1).hide_product_name)
        self.assertFalse(self.product.with_company(self.company_2).hide_product_name)
        report_description_company_1 = self._get_report_description(self.invoice)
        self.assertNotIn(self.product.name, report_description_company_1)
        invoice_company_2 = (
            self.env["account.move"]
            .with_company(self.company_2)
            .create(
                {
                    "move_type": "in_invoice",
                    "partner_id": self.partner_a.id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "product_id": self.product.id,
                                "name": self.description,
                                "quantity": 1.0,
                                "price_unit": 100.0,
                            }
                        ),
                    ],
                }
            )
        )
        self.assertFalse(invoice_company_2.invoice_line_ids.hide_product_name)
        report_description = self._get_report_description(invoice_company_2)
        self.assertIn(self.product.name, report_description)
