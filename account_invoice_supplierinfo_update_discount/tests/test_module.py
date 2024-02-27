# Copyright 2018 - Today: GRAP (http://www.grap.coop)
# Copyright Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import tagged

from odoo.addons.account_invoice_supplierinfo_update.tests.test_module import TestModule


@tagged("post_install", "-at_install")
class TestModuleDiscount(TestModule):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.line_a.write({"discount": 0.0})
        cls.line_b.write({"discount": 10.0})

    def test_supplierinfo_update_discount(self):
        vals_wizard = self.invoice.check_supplierinfo().get("context", {})

        line_ids = vals_wizard.get("default_line_ids", {})

        self.assertEqual(len(line_ids), 2)
        self.assertEqual(line_ids[0][2]["current_discount"], False)
        self.assertEqual(line_ids[0][2]["new_discount"], 0.0)
        self.assertEqual(line_ids[1][2]["current_discount"], False)
        self.assertEqual(line_ids[1][2]["new_discount"], 10.0)

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
        self.assertEqual(supplierinfo_a.discount, 0.0)

        supplierinfo_b = self.ProductSupplierinfo.search(
            [
                ("partner_id", "=", self.invoice.supplier_partner_id.id),
                ("product_tmpl_id", "=", self.product_b.product_tmpl_id.id),
            ]
        )
        self.assertEqual(len(supplierinfo_b), 1)
        self.assertEqual(supplierinfo_b.discount, 10.0)
