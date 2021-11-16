# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestAccountLineDescription(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.product_with_acc_desc = cls.env.ref("product.product_product_1")
        cls.product_without_acc_desc = cls.env.ref("product.product_product_2")

        consumable_cat = cls.env["product.category"].search(
            [("name", "=", "Consumable")]
        )

        cls.product_with_acc_desc.categ_id = consumable_cat
        cls.product_without_acc_desc.categ_id = consumable_cat

        cls.product_with_acc_desc.accounting_description = "Product1_acc_desc"

        cls.account_move = cls.env["account.move"]

    def test_invoice_line_with_accounting_description(self):
        invoice_form_acc_desc = Form(
            self.account_move.with_context(default_move_type="out_invoice")
        )
        invoice_form_acc_desc.partner_id = self.partner_1

        with invoice_form_acc_desc.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_with_acc_desc
            line_form.quantity = 1
            line_form.price_unit = 2.99

        self.invoice_acc_desc = invoice_form_acc_desc.save()
        inv_line_with_product = self.invoice_acc_desc.invoice_line_ids.filtered(
            lambda x: x.product_id
        )
        self.assertTrue(self.product_with_acc_desc.accounting_description)
        self.assertEqual(
            inv_line_with_product.name,
            self.product_with_acc_desc.accounting_description,
        )
        self.assertEqual(
            inv_line_with_product.product_id.name, inv_line_with_product.external_name
        )

    def test_invoice_line_without_accounting_description(self):
        invoice_form_no_acc_desc = Form(
            self.account_move.with_context(default_move_type="out_invoice")
        )

        invoice_form_no_acc_desc.partner_id = self.partner_1

        with invoice_form_no_acc_desc.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_without_acc_desc
            line_form.quantity = 1
            line_form.price_unit = 2.99

        self.invoice_no_acc_desc = invoice_form_no_acc_desc.save()
        inv_line_with_product = self.invoice_no_acc_desc.invoice_line_ids.filtered(
            lambda x: x.product_id
        )
        self.assertFalse(self.product_without_acc_desc.accounting_description)
        self.assertNotEqual(
            inv_line_with_product.name,
            self.product_without_acc_desc.accounting_description,
        )
        self.assertEqual(inv_line_with_product.name, self.product_without_acc_desc.name)
        self.assertEqual(
            inv_line_with_product.product_id.name, inv_line_with_product.external_name
        )
