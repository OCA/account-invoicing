# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account_invoice_supplierinfo_update.tests.test_module import TestModule


@tagged("post_install", "-at_install")
class TestModule(TestModule):
    def test_supplierinfo_update_multiplier_qty(self):
        self.ProductSupplierinfo.create(
            {
                "partner_id": self.invoice.supplier_partner_id.id,
                "product_tmpl_id": self.product_a.product_tmpl_id.id,
                "multiplier_qty": 15.0,
            }
        )

        vals_wizard = self.invoice.check_supplierinfo().get("context", {})

        line_ids = vals_wizard.get("default_line_ids", {})

        self.assertEqual(len(line_ids), 2)
        self.assertEqual(line_ids[0][2]["current_multiplier_qty"], 15.0)
        self.assertEqual(line_ids[0][2]["new_multiplier_qty"], 15.0)
        self.assertEqual(line_ids[1][2]["current_multiplier_qty"], False)
        self.assertEqual(line_ids[1][2]["new_multiplier_qty"], False)

        line_ids[0][2]["new_multiplier_qty"] = 12.0
        line_ids[1][2]["new_multiplier_qty"] = 14.0

        # Create and launch update process
        wizard = self.WizardUpdateSupplierinfo.create(
            {"line_ids": line_ids, "invoice_id": self.invoice.id}
        )

        wizard.update_supplierinfo()

        supplierinfo_a = self.ProductSupplierinfo.search(
            [
                ("partner_id", "=", self.invoice.supplier_partner_id.id),
                ("product_tmpl_id", "=", self.product_a.product_tmpl_id.id),
            ]
        )
        self.assertEqual(len(supplierinfo_a), 1)
        self.assertEqual(supplierinfo_a.multiplier_qty, 12.0)

        supplierinfo_b = self.ProductSupplierinfo.search(
            [
                ("partner_id", "=", self.invoice.supplier_partner_id.id),
                ("product_tmpl_id", "=", self.product_b.product_tmpl_id.id),
            ]
        )
        self.assertEqual(len(supplierinfo_b), 1)
        self.assertEqual(supplierinfo_b.multiplier_qty, 14.0)
