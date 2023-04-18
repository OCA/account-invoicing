# Copyright 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestModule(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.invoice = cls.in_invoice = cls.init_invoice(
            "in_invoice",
            products=[cls.product_a, cls.product_b, cls.env["product.product"]],
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        # Product A : uom_id : Unit
        cls.product_b.uom_id = cls.product_b.uom_po_id = cls.uom_unit
        cls.line_a = cls.invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == cls.product_a
        )
        # Product B : uom_id : Dozen
        cls.product_b.uom_id = cls.product_b.uom_po_id = cls.uom_dozen
        cls.line_b = cls.invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == cls.product_b
        )
        cls.line_without_product = cls.invoice.invoice_line_ids.filtered(
            lambda x: not x.product_id
        )

        cls.line_a.write(
            {"quantity": 10.0, "price_unit": 400.0, "product_uom_id": cls.uom_unit.id}
        )
        cls.line_b.write(
            {"quantity": 1.0, "price_unit": 10.0, "product_uom_id": cls.uom_dozen.id}
        )
        cls.line_without_product.write({"quantity": 1.0, "price_unit": 35.0})

        cls.WizardUpdateSupplierinfo = cls.env["wizard.update.invoice.supplierinfo"]
        cls.ProductSupplierinfo = cls.env["product.supplierinfo"]

    def test_update_pricelist_supplierinfo(self):
        # supplier invoice with pricelist supplierinfo to update and
        # product supplierinfo is on product_template

        vals_wizard = self.invoice.check_supplierinfo().get("context", {})

        line_ids = vals_wizard.get("default_line_ids", {})

        self.assertEqual(len(line_ids), 2)
        self.assertEqual(line_ids[0][2]["current_price"], False)
        self.assertEqual(line_ids[0][2]["new_price"], 400.0)
        self.assertEqual(line_ids[0][2]["current_uom_id"], False)
        self.assertEqual(line_ids[0][2]["new_uom_id"], self.uom_unit.id)
        self.assertEqual(line_ids[0][2]["current_min_quantity"], 0.0)
        self.assertEqual(line_ids[1][2]["current_price"], False)
        self.assertEqual(line_ids[1][2]["new_price"], 10.0)
        self.assertEqual(line_ids[1][2]["current_uom_id"], False)
        self.assertEqual(line_ids[1][2]["new_uom_id"], self.uom_dozen.id)

        # Change values
        line_ids[0][2]["new_min_quantity"] = 6.0

        # Create and launch update process
        wizard = self.WizardUpdateSupplierinfo.create(
            {"line_ids": line_ids, "invoice_id": self.invoice.id}
        )
        line_a = wizard.line_ids.filtered(lambda x: x.product_id == self.product_a)
        line_b = wizard.line_ids.filtered(lambda x: x.product_id == self.product_b)
        self.assertEqual(line_a.new_price, 400.0)
        self.assertEqual(line_b.new_price, 10.0)

        wizard.update_supplierinfo()

        supplierinfo_a = self.ProductSupplierinfo.search(
            [
                ("partner_id", "=", self.invoice.supplier_partner_id.id),
                ("product_tmpl_id", "=", self.product_a.product_tmpl_id.id),
            ]
        )
        self.assertEqual(len(supplierinfo_a), 1)
        self.assertEqual(supplierinfo_a.price, 400.0)
        self.assertEqual(supplierinfo_a.product_uom, self.uom_unit)
        self.assertEqual(supplierinfo_a.min_qty, 6.0)

        supplierinfo_b = self.ProductSupplierinfo.search(
            [
                ("partner_id", "=", self.invoice.supplier_partner_id.id),
                ("product_tmpl_id", "=", self.product_b.product_tmpl_id.id),
            ]
        )
        self.assertEqual(len(supplierinfo_b), 1)
        self.assertEqual(supplierinfo_b.price, 10.0)
        self.assertEqual(supplierinfo_b.product_uom, self.uom_dozen)

        # change values 400 / Unit -> 5400 / Dozen.
        # Price variation : +12.5%
        self.line_a.write({"price_unit": 5400.0, "product_uom_id": self.uom_dozen.id})
        vals_wizard = self.invoice.check_supplierinfo().get("context", {})

        line_ids = vals_wizard.get("default_line_ids", {})

        self.assertEqual(len(line_ids), 1)
        self.assertEqual(line_ids[0][2]["current_price"], 400)
        self.assertEqual(line_ids[0][2]["new_price"], 5400.0)
        self.assertEqual(line_ids[0][2]["current_uom_id"], self.uom_unit.id)
        self.assertEqual(line_ids[0][2]["new_uom_id"], self.uom_dozen.id)

        # Create and launch update process
        wizard = self.WizardUpdateSupplierinfo.create(
            {"line_ids": line_ids, "invoice_id": self.invoice.id}
        )
        line_a = wizard.line_ids.filtered(lambda x: x.product_id == self.product_a)
        self.assertEqual(line_a.cost_variation, 12.5)
        wizard.update_supplierinfo()

        self.assertEqual(supplierinfo_a.price, 5400.0)
        self.assertEqual(supplierinfo_a.product_uom, self.uom_dozen)
