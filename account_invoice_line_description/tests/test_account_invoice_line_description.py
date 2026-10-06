# Copyright 2017 - Tecnativa, S.L. - Luis M. Ontalba
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form
from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceLineDescription(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_permission = cls.env.ref(
            "account_invoice_line_description"
            ".group_use_product_description_per_inv_line"
        )
        cls.env.user.group_ids |= cls.new_permission
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.journal_sale = cls.env["account.journal"].create(
            {"name": "Test Sale Journal", "code": "TSJ", "type": "sale"}
        )
        cls.product_category = cls.env["product.category"].create(
            {
                "name": "Test Product category",
                "property_account_income_categ_id": cls.company_data[
                    "default_account_revenue"
                ].id,
                "property_account_expense_categ_id": cls.company_data[
                    "default_account_expense"
                ].id,
            }
        )
        cls.product_sale = cls.env["product.product"].create(
            {
                "name": "Test Sale Product",
                "sale_ok": True,
                "type": "consu",
                "categ_id": cls.product_category.id,
                "description_sale": "Test Description Sale",
                "lst_price": 0,
            }
        )
        cls.account = cls.company_data["default_account_revenue"]

        cls.journal_purchase = cls.env["account.journal"].create(
            {"name": "Test Purchase Journal", "code": "TPJ", "type": "purchase"}
        )
        cls.product_purchase = cls.env["product.product"].create(
            {
                "name": "Test Purchase Product",
                "purchase_ok": True,
                "type": "consu",
                "categ_id": cls.product_category.id,
                "description_purchase": "Test Description Purchase",
                "lst_price": 0,
            }
        )
        invoice_sale = Form(
            cls.env["account.move"].with_context(
                default_move_type="out_invoice",
            )
        )
        invoice_sale.partner_id = cls.partner
        invoice_sale.journal_id = cls.journal_sale
        with invoice_sale.invoice_line_ids.new() as line_form:
            line_form.name = "Test Invoice Line"
            line_form.price_unit = 500.0
            line_form.quantity = 1
            line_form.product_id = cls.product_sale
            line_form.account_id = cls.account
        cls.invoice_sale = invoice_sale.save()

        invoice_purchase = Form(
            cls.env["account.move"].with_context(
                default_move_type="in_invoice",
            )
        )
        invoice_purchase.partner_id = cls.partner
        invoice_purchase.journal_id = cls.journal_purchase
        with invoice_purchase.invoice_line_ids.new() as line_form:
            line_form.name = "Test Invoice Line"
            line_form.price_unit = 500.0
            line_form.quantity = 1
            line_form.product_id = cls.product_purchase
        cls.invoice_purchase = invoice_purchase.save()

    def test_onchange_product_id_sale(self):
        self.assertEqual(
            self.product_sale.description_sale, self.invoice_sale.invoice_line_ids.name
        )

    def test_onchange_product_id_purchase(self):
        self.assertEqual(
            self.product_purchase.description_purchase,
            self.invoice_purchase.invoice_line_ids.name,
        )

    def test_manual_description(self):
        line = self.invoice_sale.invoice_line_ids
        line.name = "Manual description"
        line._compute_name()
        self.assertEqual(line.name, "Manual description")

    def test_without_group(self):
        self.env.user.group_ids -= self.new_permission
        line = self.invoice_sale.invoice_line_ids
        line.name = False
        line._compute_name()
        self.assertEqual(
            self.invoice_sale.invoice_line_ids.name,
            f"{self.product_sale.display_name}\n{self.product_sale.description_sale}",
        )

    def test_without_description(self):
        self.product_sale.description_sale = False
        line = self.invoice_sale.invoice_line_ids
        line.name = False
        line._compute_name()
        self.assertEqual(
            self.invoice_sale.invoice_line_ids.name, self.product_sale.display_name
        )

    def test_change_product(self):
        product = self.env["product.product"].create(
            {
                "name": "New Sale Product",
                "type": "consu",
                "categ_id": self.product_category.id,
                "description_sale": "New description",
            }
        )
        self.assertEqual(
            product.with_context(
                lang=self.partner.lang or self.env.lang
            ).description_sale,
            "New description",
        )
        with Form(self.invoice_sale) as invoice:
            with invoice.invoice_line_ids.edit(0) as line:
                line.product_id = product
                self.assertEqual(line.name, "New description")
        self.assertEqual(self.invoice_sale.invoice_line_ids.product_id, product)
        self.assertEqual(self.invoice_sale.invoice_line_ids.name, "New description")
