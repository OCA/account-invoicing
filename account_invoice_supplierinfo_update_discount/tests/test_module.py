# Copyright 2018 - Today: GRAP (http://www.grap.coop)
# Copyright Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.AccountMove = self.env["account.move"]
        self.WizardUpdate = self.env["wizard.update.invoice.supplierinfo"]
        self.SupplierInfo = self.env["product.supplierinfo"]
        self.product1 = self.env.ref("product.product_product_4b")
        invoice_form = Form(self.AccountMove.with_context(default_type="in_invoice"))
        invoice_form.partner_id = self.env.ref("base.res_partner_12")
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product1
            line_form.quantity = 10.0
            line_form.price_unit = 400.0
            line_form.discount = 10.0
        self.invoice = invoice_form.save()

    # Test Section
    def test_discount(self):
        # Launch and confirm Wizard
        lines_for_update = self.invoice._get_update_supplierinfo_lines()
        wizard = self.WizardUpdate.with_context(
            default_line_ids=lines_for_update, default_invoice_id=self.invoice.id,
        ).create({})
        wizard.update_supplierinfo()

        # Check Regressions
        supplierinfo = self.SupplierInfo.search(
            [
                ("product_tmpl_id", "=", self.product1.product_tmpl_id.id),
                ("name", "=", self.invoice.partner_id.id),
            ]
        )

        self.assertEqual(
            len(supplierinfo),
            1,
            "Regression : Confirming wizard should have create a supplierinfo",
        )

        self.assertEqual(
            supplierinfo.discount,
            10,
            "Confirming wizard should have update main discount",
        )
