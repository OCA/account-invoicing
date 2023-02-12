# © 2023 FactorLibre - Javier Iniesta <javier.iniesta@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoice(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        invoice_date = fields.Date.today()
        cls.in_invoice = cls.init_invoice(
            "in_invoice",
            partner=cls.partner_a,
            invoice_date=invoice_date,
            products=cls.product_a,
        )
        cls.out_invoice = cls.init_invoice(
            "out_invoice",
            partner=cls.partner_a,
            invoice_date=invoice_date,
            products=cls.product_a,
        )
        cls.currency_euro_id = cls.env.ref("base.EUR").id
        cls.currency_euro_rate = 0.5
        cls.env["res.currency.rate"].create(
            {
                "currency_id": cls.currency_euro_id,
                "name": invoice_date,
                "rate": cls.currency_euro_rate,
            }
        )

    def test_prepare_tax_totals_in_invoice(self):
        self.assertFalse(
            self.in_invoice.tax_totals.get("display_company_currency_taxes")
        )
        for data_list in self.in_invoice.tax_totals["groups_by_subtotal"].values():
            for group in data_list:
                self.assertFalse(
                    group.get("formatted_tax_group_amount_company_currency")
                )
        self.in_invoice.currency_id = self.currency_euro_id
        self.assertTrue(
            self.in_invoice.tax_totals.get("display_company_currency_taxes")
        )
        for data_list in self.in_invoice.tax_totals["groups_by_subtotal"].values():
            for group in data_list:
                self.assertTrue(
                    group.get("formatted_tax_group_amount_company_currency")
                )

    def test_prepare_tax_totals_out_invoice(self):
        self.assertFalse(
            self.out_invoice.tax_totals.get("display_company_currency_taxes")
        )
        for data_list in self.out_invoice.tax_totals["groups_by_subtotal"].values():
            for group in data_list:
                self.assertFalse(
                    group.get("formatted_tax_group_amount_company_currency")
                )
        self.out_invoice.currency_id = self.currency_euro_id
        self.assertTrue(
            self.out_invoice.tax_totals.get("display_company_currency_taxes")
        )
        for data_list in self.out_invoice.tax_totals["groups_by_subtotal"].values():
            for group in data_list:
                self.assertTrue(
                    group.get("formatted_tax_group_amount_company_currency")
                )
