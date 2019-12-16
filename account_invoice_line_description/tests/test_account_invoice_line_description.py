# Copyright 2017 - Tecnativa, S.L. - Luis M. Ontalba
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests.common import SavepointCase, at_install, post_install


@at_install(False)
@post_install(True)
class TestAccountInvoiceLineDescription(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceLineDescription, cls).setUpClass()
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
        cls.invoice_sale_vals = [
            (
                0,
                0,
                {
                    "product_id": cls.product_sale.id,
                    "name": "Test Invoice Line",
                    "account_id": cls.account.id,
                    "price_unit": 500.00,
                },
            )
        ]
        cls.invoice_sale = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "journal_id": cls.journal_sale.id,
                "type": "out_invoice",
                "invoice_line_ids": cls.invoice_sale_vals,
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
        cls.invoice_purchase_vals = [
            (
                0,
                0,
                {
                    "product_id": cls.product_purchase.id,
                    "name": "Test Invoice Line",
                    "account_id": cls.account.id,
                    "price_unit": 500.00,
                },
            )
        ]
        cls.invoice_purchase = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "journal_id": cls.journal_purchase.id,
                "type": "in_invoice",
                "invoice_line_ids": cls.invoice_purchase_vals,
            }
        )

    def test_onchange_product_id_sale(self):
        self.invoice_sale.invoice_line_ids._onchange_product_id()
        self.assertEqual(
            self.product_sale.description_sale, self.invoice_sale.invoice_line_ids.name
        )

    def test_onchange_product_id_purchase(self):
        self.invoice_purchase.invoice_line_ids._onchange_product_id()
        self.assertEqual(
            self.product_purchase.description_purchase,
            self.invoice_purchase.invoice_line_ids.name,
        )
