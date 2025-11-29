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

    def test_get_the_right_variant_supplierinfo(self):
        # Variant the product A and set a price on variation 1
        tmpl_a = self.product_a.product_tmpl_id
        tmpl_a.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.env.ref(
                                "product.product_attribute_2"
                            ).id,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        self.env.ref(
                                            "product.product_attribute_value_3"
                                        ).id,
                                        self.env.ref(
                                            "product.product_attribute_value_4"
                                        ).id,
                                    ],
                                )
                            ],
                        },
                    )
                ]
            }
        )
        product_a_1, product_a_2 = tmpl_a.product_variant_ids

        supplier_product_a_1 = self.env["product.supplierinfo"].create(
            [
                {
                    "partner_id": self.invoice.supplier_partner_id.id,
                    "product_tmpl_id": tmpl_a.id,
                    "product_id": product_a_1.id,
                    "price": 30,
                }
            ]
        )

        # Set the variation 2 on the invoice and run the wizard
        self.line_a.write({"product_id": product_a_2, "price_unit": 400})
        vals_wizard = self.invoice.check_supplierinfo().get("context", {})
        line_ids = vals_wizard.get("default_line_ids", {})

        self.assertEqual(line_ids[0][2]["current_price"], False)
        self.assertEqual(line_ids[0][2]["new_price"], 400.0)

        wizard = self.WizardUpdateSupplierinfo.create(
            {"line_ids": line_ids, "invoice_id": self.invoice.id}
        )
        wizard.update_supplierinfo()

        # Supplier of product_a_1 should be not updated and a new supplierinfo
        # have been created (to make it simple supplierinfo are always created
        # on template)
        self.assertEqual(supplier_product_a_1.price, 30)
        self.assertEqual(len(tmpl_a.seller_ids), 2)
        self.assertEqual(tmpl_a.seller_ids[1].price, 400)
        self.assertFalse(tmpl_a.seller_ids[1].product_id)

    def test_get_the_right_qty_supplierinfo(self):
        tmpl_a = self.product_a.product_tmpl_id
        self.env["product.supplierinfo"].create(
            [
                {
                    "partner_id": self.invoice.supplier_partner_id.id,
                    "product_tmpl_id": tmpl_a.id,
                    "price": 500,
                    "min_qty": 0,
                },
                {
                    "partner_id": self.invoice.supplier_partner_id.id,
                    "product_tmpl_id": tmpl_a.id,
                    "price": 300,
                    "min_qty": 20,
                },
            ]
        )

        vals_wizard = self.invoice.check_supplierinfo().get("context", {})
        line_ids = vals_wizard.get("default_line_ids", {})

        self.assertEqual(line_ids[0][2]["current_price"], 500)
        self.assertEqual(line_ids[0][2]["new_price"], 400.0)

        wizard = self.WizardUpdateSupplierinfo.create(
            {"line_ids": line_ids, "invoice_id": self.invoice.id}
        )
        wizard.update_supplierinfo()

        self.assertEqual(len(tmpl_a.seller_ids), 2)
        self.assertEqual(tmpl_a.seller_ids[0].price, 300)
        self.assertEqual(tmpl_a.seller_ids[1].price, 400)

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
