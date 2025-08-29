# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form, SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestAccountInvoiceSupplierInfoDiscount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AccountInvoice = cls.env["account.move"]
        cls.WizardUpdate = cls.env["wizard.update.invoice.supplierinfo"]
        cls.SupplierInfo = cls.env["product.supplierinfo"]

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Test product",
            }
        )
        cls.env.ref("uom.product_uom_unit")
        cls.account = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_expenses").id,
                ),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )

        invoice_form = Form(
            cls.env["account.move"].with_context(default_type="in_invoice")
        )
        invoice_form.partner_id = cls.env["res.partner"].create(
            {
                "name": "Mr. Odoo",
            }
        )
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = cls.product1
            line_form.quantity = 10.0
            line_form.price_unit = 400.0
            line_form.discount = 10.0
            line_form.discount2 = 20.0
            line_form.discount3 = 30.0
            line_form.account_id = cls.account
        cls.invoice = invoice_form.save()

    # Test Section
    def test_01_triple_discount(self):
        # Launch and confirm Wizard
        lines_for_update = self.invoice._get_update_supplierinfo_lines()
        wizard = self.WizardUpdate.with_context(
            default_line_ids=lines_for_update, default_invoice_id=self.invoice.id
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
            "Regression : Confirming wizard should have update main discount",
        )

        # Check Correct Discounts
        self.assertEqual(
            supplierinfo.discount2,
            20,
            "Confirming wizard should have update discount #2",
        )
        self.assertEqual(
            supplierinfo.discount3,
            30,
            "Confirming wizard should have update discount #3",
        )
