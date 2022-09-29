# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.fields import first
from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestInvoicePriceUntaxed(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
            )
        )
        cls.tmpl_obj = cls.env["product.template"]
        cls.prod_obj = cls.env["product.product"]
        cls.company_obj = cls.env["res.company"]
        cls.account_move_line_obj = cls.env["account.move.line"]
        cls.precision = cls.env["decimal.precision"].precision_get(
            cls.account_move_line_obj._fields["price_unit"]._digits
        )
        cls.company = cls.env.ref("base.main_company")
        vals = {
            "name": "Company 2",
        }
        cls.company_2 = cls.company_obj.create(vals)
        cls.env["account.chart.template"].browse(1).with_company(
            cls.company_2
        ).try_loading()

        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.write({"company_id": False})
        cls.journal_sale_1 = cls.env["account.journal"].create(
            {
                "name": "Test Sale Journal",
                "code": "TSJ",
                "type": "sale",
                "company_id": cls.company.id,
            }
        )
        cls.journal_sale_2 = cls.env["account.journal"].create(
            {
                "name": "Test Sale Journal",
                "code": "TSJ",
                "type": "sale",
                "company_id": cls.company_2.id,
            }
        )
        cls.tax1 = cls.env["account.tax"].create(
            {
                "name": "Test Taxe 1",
                "type_tax_use": "sale",
                "company_id": cls.company.id,
                "amount_type": "percent",
                "amount": 15,
                "price_include": False,
            }
        )
        cls.tax2 = cls.env["account.tax"].create(
            {
                "name": "Test Taxe 1",
                "type_tax_use": "sale",
                "company_id": cls.company_2.id,
                "amount_type": "percent",
                "amount": 15,
                "price_include": True,
            }
        )
        cls.tmpl = cls.tmpl_obj.create(
            {
                "name": "NewTmpl",
                "taxes_id": [(4, cls.tax1.id), (4, cls.tax2.id)],
                "list_price": 115.0,
            }
        )
        cls.account = cls.env["account.account"].search(
            [("user_type_id.type", "=", "other"), ("internal_group", "=", "income")],
            limit=1,
        )
        cls.account_2 = cls.account.copy({"company_id": cls.company_2.id})
        cls.product = cls.tmpl.product_variant_ids[0]
        cls.product.with_company(
            cls.company_2
        ).property_account_income_id = cls.account_2
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.user_demo.write(
            {
                "company_ids": [(4, cls.company.id), (4, cls.company_2.id)],
                "groups_id": [(4, cls.env.ref("account.group_account_invoice").id)],
            }
        )

    def test_invoice_with_product_main_company(self):
        self.user_demo.write(
            {
                "company_id": self.company.id,
            }
        )

        self.invoice = (
            self.env["account.move"]
            .with_user(self.user_demo)
            .with_company(self.company)
            .create(
                {
                    "partner_id": self.partner.id,
                    "journal_id": self.journal_sale_1.id,
                    "move_type": "out_invoice",
                }
            )
        )
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.new() as invoice_line:
                invoice_line.product_id = self.product
        invoice_line = first(self.invoice.invoice_line_ids)
        self.assertEqual(invoice_line.price_unit, 115)
        self.assertEqual(invoice_line.price_unit_untaxed, 115)

    def test_invoice_with_product_company2(self):
        self.user_demo.write(
            {
                "company_id": self.company_2.id,
            }
        )
        self.invoice = (
            self.env["account.move"]
            .with_user(self.user_demo)
            .with_company(self.company_2)
            .create(
                {
                    "partner_id": self.partner.id,
                    "journal_id": self.journal_sale_2.id,
                    "move_type": "out_invoice",
                }
            )
        )
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.new() as invoice_line:
                invoice_line.product_id = self.product
        invoice_line = first(self.invoice.invoice_line_ids)
        self.assertEqual(invoice_line.price_unit, 115)
        self.assertEqual(invoice_line.price_unit_untaxed, 100)

    def test_invoice_with_decimal_precision(self):
        """
        Set tax with price include False
        Set the product price to 118.573
        Set product price precision to 3
        Check prices are equivalent (price_unit == price_unit_untaxed) with
        same
        """
        self.tax2.price_include = False
        self.user_demo.write(
            {
                "company_id": self.company_2.id,
            }
        )
        self.invoice = (
            self.env["account.move"]
            .with_user(self.user_demo)
            .with_company(self.company_2)
            .create(
                {
                    "partner_id": self.partner.id,
                    "journal_id": self.journal_sale_2.id,
                    "move_type": "out_invoice",
                }
            )
        )
        precision = self.env["decimal.precision"].search(
            [("name", "=", "Product Price")]
        )
        precision.write({"digits": 3})
        self.product.list_price = 118.573
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.new() as invoice_line:
                invoice_line.product_id = self.product
        invoice_line = first(self.invoice.invoice_line_ids)
        self.assertAlmostEquals(invoice_line.price_unit, 118.573, places=self.precision)
        self.assertAlmostEquals(
            invoice_line.price_unit_untaxed, 118.573, places=self.precision
        )
