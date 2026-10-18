from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestAccountLineDescription(TransactionCase):
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

        cls.product_with_acc_desc.accounting_description = "Virtual Interior Design"

    # -------------------------------------------------------------------------
    # Test: product WITH accounting description
    # -------------------------------------------------------------------------
    def test_invoice_line_with_accounting_description(self):
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = self.partner_1

        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_with_acc_desc
            line_form.quantity = 1
            line_form.price_unit = 2.99

        invoice = invoice_form.save()
        line = invoice.invoice_line_ids.filtered(lambda inv_line: inv_line.product_id)

        # Force English for reading both values
        line_name_en = line.with_context(lang="en_US").name
        acc_desc_en = self.product_with_acc_desc.with_context(
            lang="en_US"
        ).accounting_description

        self.assertEqual(line_name_en, acc_desc_en)
        self.assertEqual(line.product_id.name, line.external_name)

    # -------------------------------------------------------------------------
    # Test: product WITHOUT accounting description
    # -------------------------------------------------------------------------
    def test_invoice_line_without_accounting_description(self):
        # Build everything in English context
        env_en = self.env(context=dict(self.env.context, lang="en_US"))

        partner_en = env_en.ref("base.res_partner_1")
        product_en = env_en.ref("product.product_product_2")

        # Ensure category in the English context
        consumable_cat = env_en["product.category"].search(
            [("name", "=", "Consumable")]
        )
        product_en.categ_id = consumable_cat

        invoice_form = Form(
            env_en["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = partner_en

        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = product_en
            line_form.quantity = 1
            line_form.price_unit = 2.99

        invoice = invoice_form.save()
        line = invoice.invoice_line_ids.filtered(lambda inv_line: inv_line.product_id)

        # Force English for comparison
        line_name_en = line.with_context(lang="en_US").name
        product_name_en = product_en.with_context(lang="en_US").name

        self.assertFalse(product_en.accounting_description)
        self.assertEqual(line_name_en, product_name_en)
        self.assertEqual(line.product_id.name, line.external_name)
