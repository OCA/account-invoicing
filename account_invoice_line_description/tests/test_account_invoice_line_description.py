# Copyright 2017 - Tecnativa, S.L. - Luis M. Ontalba
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountInvoiceLineDescription(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_permission = cls.env.ref(
            "account_invoice_line_description"
            ".group_use_product_description_per_inv_line"
        )
        cls.env.user.groups_id |= cls.new_permission
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.journal_sale = cls.env["account.journal"].create(
            {"name": "Test Sale Journal", "code": "TSJ", "type": "sale"}
        )
        cls.product_category = cls.env["product.category"].create(
            {"name": "Test Product category"}
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
        cls.account_type_regular = cls.env["account.account.type"].create(
            {"name": "regular", "type": "other", "internal_group": "income"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "TA",
                "user_type_id": cls.account_type_regular.id,
            }
        )

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
