# Copyright 2014 ToDay Akretion (http://www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestProductIdChange(AccountingTestCase):
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
                "lst_price": "15000",
                "taxes_id": [(6, 0, [tax_sale.id])],
                "property_account_income_id": self.account_revenue.id,
            }
        )
        product = self.product_model.create(
            {"product_tmpl_id": product_tmpl.id, "standard_price": "12000"}
        )
        fp = self.fiscal_position_model.create(
            {"name": "fiscal position export", "sequence": 1}
        )

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
                "invoice_payment_ref": "invoice to client",
                "type": "out_invoice",
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
        out_invoice.fiscal_position_id = fp
        out_invoice.with_context(check_move_validity=False).fiscal_position_change()
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

        # We test it the same but using taxes with price included

        # Step 1: create two taxes with price included
        tax_sale_ip = self.tax_model.create(
            {
                "name": "Sale tax Included",
                "type_tax_use": "sale",
                "amount": "20.00",
                "price_include": True,
                "amount_type": "division",
            }
        )
        tax_export_sale_ip = self.tax_model.create(
            {
                "name": "Export tax Included",
                "type_tax_use": "sale",
                "amount": "50.00",
                "price_include": True,
                "amount_type": "division",
            }
        )

        # Step 2: Create a new fiscal position that do the mapping between this
        # new two taxes with price include
        fp_ip = self.fiscal_position_model.create(
            {"name": "fiscal position export", "sequence": 1}
        )
        fp_tax_sale_ip = self.fiscal_position_tax_model.create(
            {
                "position_id": fp_ip.id,
                "tax_src_id": tax_sale_ip.id,
                "tax_dest_id": tax_export_sale_ip.id,
            }
        )

        # Step 3: Configure the Sale Tax Included as the default value of the
        # product
        product_tmpl.write({"taxes_id": [(6, 0, [tax_sale_ip.id])]})

        # Step 4: Create a Invoice in roder to indentify that was created
        # normaly with the product configured tax of type price included
        out_invoice = self.invoice_model.create(
            {
                "partner_id": partner.id,
                "invoice_payment_ref": "invoice to client",
                "type": "out_invoice",
                "invoice_date": time.strftime("%Y") + "-04-01",
            }
        )
        out_line = self.invoice_line_model.with_context(
            check_move_validity=False
        ).create(
            {
                "product_id": product.id,
                "move_id": out_invoice.id,
                "account_id": self.account_revenue.id,
            }
        )
        out_line._onchange_product_id()
        self.assertEqual(
            out_line.tax_ids[0],
            tax_sale_ip,
            "The sale tax off invoice line must be the same of product",
        )

        # Step 5: We modify the invoice to add the new fiscal position with
        # taxes included
        out_invoice.fiscal_position_id = fp_ip
        out_invoice.with_context(check_move_validity=False).fiscal_position_change()
        self.assertEqual(
            out_line.tax_ids[0],
            fp_tax_sale_ip.tax_dest_id,
            "The sale tax of invoice line must be changed by fiscal position",
        )

        # Step 6: Check that the price unit and subtotal do actually proper
        # change to the correct amounts
        self.assertEqual(
            out_line.price_subtotal,
            7500.0,
            "The subtotal should be the price unit minus the dest tax amount",
        )
