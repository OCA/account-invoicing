# Copyright 2014 ToDay Akretion (http://www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestProductIdChange(AccountTestInvoicingCommon):
    """Test that when an included tax is mapped by a fiscal position,
    when position fiscal change taxes and account wil be update on
    invoice lines.
    """

    def setUp(self):
        super(TestProductIdChange, self).setUp()
        self.invoice_model = self.env["account.move"]
        self.fiscal_position_model = self.env["account.fiscal.position"]
        self.fiscal_position_tax_model = self.env["account.fiscal.position.tax"]
        self.fiscal_position_account_model = self.env["account.fiscal.position.account"]
        self.tax_model = self.env["account.tax"]
        self.account_model = self.env["account.account"]
        self.pricelist_model = self.env["product.pricelist"]
        self.res_partner_model = self.env["res.partner"]
        self.product_tmpl_model = self.env["product.template"]
        self.product_model = self.env["product.product"]
        self.invoice_line_model = self.env["account.move.line"]
        self.account_user_type = self.env.ref("account.data_account_type_revenue")
        self.account_receivable = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        self.account_revenue = self.env["account.account"].search(
            [("user_type_id", "=", self.account_user_type.id)], limit=1
        )

    def test_fiscal_position_id_change(self):
        partner = self.res_partner_model.create(dict(name="George"))
        account_export_id = self.account_model.sudo().create(
            {
                "code": "710000-account_invoice_fiscal_position_update",
                "name": "customer export account",
                "user_type_id": self.account_user_type.id,
                "reconcile": True,
            }
        )
        tax_sale = self.tax_model.create(
            {"name": "Sale tax", "type_tax_use": "sale", "amount": "20.00"}
        )

        tax_export_sale = self.tax_model.create(
            {"name": "Export tax", "type_tax_use": "sale", "amount": "0.00"}
        )

        product_tmpl = self.product_tmpl_model.create(
            {
                "name": "Car",
                "list_price": "15000",
                "taxes_id": [(6, 0, [tax_sale.id])],
                "property_account_income_id": self.account_revenue.id,
            }
        )
        product = product_tmpl.product_variant_id
        product.standard_price = 12000
        fp = self.fiscal_position_model.create(
            {"name": "fiscal position export", "sequence": 1}
        )
        fp2 = self.fiscal_position_model.create(
            {"name": "fiscal position import", "sequence": 1}
        )
        partner.write({"property_account_position_id": fp.id})

        fp_tax_sale = self.fiscal_position_tax_model.create(
            {
                "position_id": fp.id,
                "tax_src_id": tax_sale.id,
                "tax_dest_id": tax_export_sale.id,
            }
        )

        fp_account = self.fiscal_position_account_model.create(
            {
                "position_id": fp.id,
                "account_src_id": self.account_revenue.id,
                "account_dest_id": account_export_id.id,
            }
        )

        out_invoice = self.invoice_model.create(
            {
                "partner_id": partner.id,
                "ref": "invoice to client",
                "move_type": "out_invoice",
                "invoice_date": time.strftime("%Y") + "-04-01",
            }
        )
        out_line = self.invoice_line_model.with_context(
            check_move_validity=False
        ).create(
            {
                "product_id": product.id,
                "price_unit": 15000,
                "quantity": 1,
                "move_id": out_invoice.id,
                "name": "Car",
                "account_id": self.account_revenue.id,
            }
        )

        out_line._onchange_product_id()
        self.assertEqual(
            out_line.tax_ids[0],
            tax_sale,
            "The sale tax off invoice line must be the same of product",
        )
        out_invoice.fiscal_position_id = fp2
        # change the partner with other FP
        out_invoice.with_context(check_move_validity=False)._onchange_partner_id()
        self.assertEqual(
            out_line.tax_ids[0],
            fp_tax_sale.tax_dest_id,
            "The sale tax of invoice line must be changed by fiscal position",
        )
        self.assertEqual(
            out_line.account_id,
            fp_account.account_dest_id,
            "The account revenue of invoice line must be changed by fiscal position",
        )
        # Test warning due to lines without product
        self.invoice_line_model.with_context(check_move_validity=False).create(
            {
                "name": "Line without product",
                "price_unit": 100,
                "quantity": 1,
                "move_id": out_invoice.id,
                "account_id": self.account_revenue.id,
            }
        )
        onchange_result = out_invoice.with_context(
            check_move_validity=False
        )._onchange_fiscal_position_id_account_invoice_fiscal_position_invoice()
        self.assertTrue(type(onchange_result) == dict)
        self.assertEqual(list(onchange_result.keys()), ["warning"])

        # for all lines without product
        out_invoice_without_prd = self.invoice_model.create(
            {
                "partner_id": partner.id,
                "ref": "invoice to client",
                "move_type": "out_invoice",
                "invoice_date": time.strftime("%Y") + "-04-01",
            }
        )
        # Test warning due to lines without product
        self.invoice_line_model.with_context(check_move_validity=False).create(
            {
                "name": "Line without product",
                "price_unit": 100,
                "quantity": 1,
                "move_id": out_invoice_without_prd.id,
                "account_id": self.account_revenue.id,
            }
        )
        onchange_result = out_invoice_without_prd.with_context(
            check_move_validity=False
        )._onchange_fiscal_position_id_account_invoice_fiscal_position_invoice()
        self.assertTrue(type(onchange_result) == dict)
        self.assertEqual(list(onchange_result.keys()), ["warning"])
