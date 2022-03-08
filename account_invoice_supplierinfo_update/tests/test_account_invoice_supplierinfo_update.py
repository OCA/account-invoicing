# Copyright 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import Form, TransactionCase


class Tests(TransactionCase):
    def setUp(self):
        super(Tests, self).setUp()
        self.wizard_obj = self.env["wizard.update.invoice.supplierinfo"]
        self.supplierinfo_obj = self.env["product.supplierinfo"]
        self.invoice_model = self.env["account.move"]
        journal_model = self.env["account.journal"]
        self.journal = journal_model.search([("type", "=", "purchase")], limit=1)
        self.product1 = self.env.ref("product.product_product_4b")
        self.product2 = self.env.ref("product.product_delivery_01")
        unit = self.env.ref("uom.product_uom_unit")
        self.currency = self.env.ref("base.GBP")
        self.journal.write({"currency_id": self.currency.id})

        invoice_form = Form(self.invoice_model.with_context(default_type="in_invoice"))
        invoice_form.partner_id = self.env.ref("base.res_partner_12")
        invoice_form.journal_id = self.journal
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product1
            line_form.quantity = 10.0
            line_form.product_uom_id = unit
            line_form.price_unit = 400.0
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "line without product"
            line_form.quantity = 1.0
            line_form.product_uom_id = unit
            line_form.price_unit = 35.0
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product2
            line_form.quantity = 1.0
            line_form.product_uom_id = unit
            line_form.price_unit = 10.0
        self.invoice = invoice_form.save()

    def test_with_update_pricelist_supplierinfo_on_product_template(self):
        # supplier invoice with pricelist supplierinfo to update and
        # product supplierinfo is on product_template

        vals_wizard = self.invoice.check_supplierinfo().get("context", {})

        line_ids = vals_wizard.get("default_line_ids", {})
        invoice_id = vals_wizard.get("default_invoice_id", {})

        self.assertEquals(len(line_ids), 2)
        self.assertEquals(line_ids[0][2]["current_price"], False)
        self.assertEquals(line_ids[0][2]["new_price"], 400.0)

        # Create and launch update process
        wizard = self.wizard_obj.create(
            {"line_ids": line_ids, "invoice_id": invoice_id}
        )
        self.assertEquals(wizard.line_ids[1].new_price, 10.0)
        wizard.update_supplierinfo()

        supplierinfos1 = self.supplierinfo_obj.search(
            [
                ("name", "=", self.invoice.supplier_partner_id.id),
                (
                    "product_tmpl_id",
                    "=",
                    self.invoice.invoice_line_ids[0].product_id.product_tmpl_id.id,
                ),
            ]
        )
        self.assertEquals(len(supplierinfos1), 1)
        self.assertEqual(supplierinfos1.currency_id, self.currency)

        self.assertEquals(supplierinfos1.price, 400.0)

        supplierinfos2 = self.supplierinfo_obj.search(
            [
                ("name", "=", self.invoice.supplier_partner_id.id),
                (
                    "product_tmpl_id",
                    "=",
                    self.invoice.invoice_line_ids[2].product_id.product_tmpl_id.id,
                ),
            ]
        )
        self.assertEquals(len(supplierinfos2), 1)

        self.assertEquals(supplierinfos2.price, 10.0)

    def test_update_pricelist_supplierinfo_uom_conversion(self):
        """Price is converted to the product's purchase UOM"""
        self.product1.uom_po_id = self.env.ref("uom.product_uom_dozen")
        invoice_line = self.invoice.invoice_line_ids.filtered(
            lambda ail: ail.product_id == self.product1
        )
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.price_unit = 33.0
        wizard = self.wizard_obj.with_context(
            self.invoice.check_supplierinfo()["context"]
        ).create({})
        line = wizard.line_ids.filtered(lambda line: line.product_id == self.product1)

        # Prices are converted to the purchase UOM.
        # 33 per unit equals 396 per dozen
        self.assertEquals(line.new_price, 396.0)

        wizard.update_supplierinfo()
        supplierinfo = self.supplierinfo_obj.search(
            [
                ("name", "=", self.invoice.supplier_partner_id.id),
                ("product_tmpl_id", "=", self.product1.product_tmpl_id.id),
            ]
        )
        self.assertEquals(supplierinfo.price, 396.0)
        self.assertTrue(invoice_line._is_correct_price(supplierinfo))
