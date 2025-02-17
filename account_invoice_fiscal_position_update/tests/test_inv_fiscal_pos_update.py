# Copyright 2014 ToDay Akretion (http://www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestProductIdChange(AccountTestInvoicingCommon):
    """Test that when an included tax is mapped by a fiscal position,
    when position fiscal change taxes and account wil be update on
    invoice lines.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice_model = cls.env["account.move"]
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        cls.fiscal_position_tax_model = cls.env["account.fiscal.position.tax"]
        cls.fiscal_position_account_model = cls.env["account.fiscal.position.account"]
        cls.tax_model = cls.env["account.tax"]
        cls.account_model = cls.env["account.account"]
        cls.pricelist_model = cls.env["product.pricelist"]
        cls.res_partner_model = cls.env["res.partner"]
        cls.product_tmpl_model = cls.env["product.template"]
        cls.product_model = cls.env["product.product"]
        cls.invoice_line_model = cls.env["account.move.line"]
        cls.account_receivable = cls.env["account.account"].search(
            [("account_type", "=", "asset_receivable")], limit=1
        )
        cls.account_revenue = cls.env["account.account"].search(
            [("account_type", "=", "income")], limit=1
        )
        cls.partner = cls.res_partner_model.create(dict(name="George"))
        cls.tax_sale_excl = cls.tax_model.create(
            {
                "name": "Sale tax B2B",
                "type_tax_use": "sale",
                "amount": "20.00",
            }
        )
        cls.tax_sale_incl = cls.tax_model.create(
            {
                "name": "Sale tax B2C",
                "type_tax_use": "sale",
                "amount": "20.00",
                "price_include_override": "tax_included",
            }
        )
        cls.tax_sale_export = cls.tax_model.create(
            {"name": "Sale tax zero", "type_tax_use": "sale", "amount": "0.00"}
        )
        product_tmpl = cls.product_tmpl_model.create(
            {
                "name": "Car",
                "property_account_income_id": cls.account_revenue.id,
            }
        )
        cls.product = product_tmpl.product_variant_id

    def test_fiscal_position_id_change(self):
        account_export_id = self.account_model.sudo().create(
            {
                "code": "710000AccountInvoiceFiscalPositionUpdate",
                "name": "customer export account",
                "account_type": "income",
                "reconcile": True,
            }
        )
        self.product.taxes_id = self.tax_sale_excl
        self.product.lst_price = 12000
        fp = self.fiscal_position_model.create(
            {"name": "fiscal position export", "sequence": 1}
        )
        fp2 = self.fiscal_position_model.create(
            {"name": "fiscal position import", "sequence": 1}
        )
        self.partner.write({"property_account_position_id": fp2.id})

        fp_tax_sale = self.fiscal_position_tax_model.create(
            {
                "position_id": fp.id,
                "tax_src_id": self.tax_sale_excl.id,
                "tax_dest_id": self.tax_sale_export.id,
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
                "partner_id": self.partner.id,
                "ref": "invoice to client",
                "move_type": "out_invoice",
                "invoice_date": time.strftime("%Y") + "-04-01",
            }
        )
        out_line = self.invoice_line_model.with_context(
            check_move_validity=False
        ).create(
            {
                "product_id": self.product.id,
                "price_unit": 15000,
                "quantity": 1,
                "move_id": out_invoice.id,
                "name": "Car",
            }
        )
        self.assertEqual(
            out_line.tax_ids[0],
            self.tax_sale_excl,
            "The sale tax off invoice line must be the same of product",
        )
        out_invoice.fiscal_position_id = fp
        out_invoice.with_context(
            check_move_validity=False
        )._onchange_fiscal_position_id_account_invoice_fiscal_position_invoice()
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
            }
        )
        onchange_result = out_invoice.with_context(
            check_move_validity=False
        )._onchange_fiscal_position_id_account_invoice_fiscal_position_invoice()
        self.assertTrue(isinstance(onchange_result, dict))
        self.assertEqual(list(onchange_result.keys()), ["warning"])

        # for all lines without product
        out_invoice_without_prd = self.invoice_model.create(
            {
                "partner_id": self.partner.id,
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
            }
        )
        onchange_result = out_invoice_without_prd.with_context(
            check_move_validity=False
        )._onchange_fiscal_position_id_account_invoice_fiscal_position_invoice()
        self.assertTrue(isinstance(onchange_result, dict))
        self.assertEqual(list(onchange_result.keys()), ["warning"])

    def _test_price_conversion(
        self,
        original_tax,
        mapped_tax,
        product_price,
        original_subtotal_price,
        original_total_price,
        mapped_subtotal_price,
        mapped_total_price,
    ):
        """Test price conversion for a specific tax mapping"""
        self.product.taxes_id = original_tax
        self.product.lst_price = product_price
        fp = self.fiscal_position_model.create(
            {
                "name": __name__,
                "sequence": 99,
                "tax_ids": [
                    Command.create(
                        {
                            "tax_src_id": original_tax.id,
                            "tax_dest_id": mapped_tax.id,
                        }
                    ),
                ],
            }
        )
        out_invoice = self.invoice_model.create(
            {
                "partner_id": self.partner.id,
                "ref": "invoice to client",
                "move_type": "out_invoice",
                "invoice_date": time.strftime("%Y") + "-04-01",
                "fiscal_position_id": False,
            }
        )
        # Create a line without fiscal position
        out_line = self.invoice_line_model.with_context(
            check_move_validity=False
        ).create(
            {
                "product_id": self.product.id,
                "quantity": 1,
                "move_id": out_invoice.id,
                "name": "Car",
            }
        )
        self.assertEqual(out_line.tax_ids, original_tax)
        self.assertEqual(out_line.price_subtotal, original_subtotal_price)
        self.assertEqual(out_line.price_total, original_total_price)
        out_invoice.fiscal_position_id = fp

        # Create a line with fiscal position (checking Odoo standard behaviour)
        out_line2 = self.invoice_line_model.with_context(
            check_move_validity=False
        ).create(
            {
                "product_id": self.product.id,
                "quantity": 1,
                "move_id": out_invoice.id,
                "name": "Car",
            }
        )
        self.assertEqual(out_line2.tax_ids, mapped_tax)
        self.assertEqual(out_line2.price_subtotal, mapped_subtotal_price)
        self.assertEqual(out_line2.price_total, mapped_total_price)

        # Check behaviour when applying the change of fiscal position
        out_invoice.with_context(
            check_move_validity=False
        )._onchange_fiscal_position_id_account_invoice_fiscal_position_invoice()
        self.assertEqual(out_line.tax_ids, mapped_tax)
        # Result is the same as Odoo standard behaviour
        self.assertEqual(out_line.price_subtotal, mapped_subtotal_price)
        self.assertEqual(out_line.price_total, mapped_total_price)

    def test_price_incl_to_zero(self):
        """Test conversion of price from tax incl to zero (export) tax.

        We don't expect the subtotal price of the line to change.
        """
        self._test_price_conversion(
            self.tax_sale_incl,
            self.tax_sale_export,
            product_price=1000,
            original_subtotal_price=833.33,
            original_total_price=1000,
            # Subtotal is not changed, conversion is successful
            mapped_subtotal_price=833.33,
            mapped_total_price=833.33,
        )

    def test_price_incl_to_excl(self):
        """Test conversion of price from tax incl. to tax excl.

        We don't expect the subtotal price of the line to change.
        """
        self._test_price_conversion(
            self.tax_sale_incl,
            self.tax_sale_excl,
            product_price=1000,
            original_subtotal_price=833.33,
            original_total_price=1000,
            # Subtotal is not changed, conversion is successful
            mapped_subtotal_price=833.33,
            mapped_total_price=1000,
        )

    def test_price_zero_to_incl(self):
        """Test conversion of price from tax zero to tax incl.

        NB. as per Odoo standard behaviour, the subtotal of the price decreases.
        """
        self._test_price_conversion(
            self.tax_sale_export,
            self.tax_sale_incl,
            product_price=833.33,
            original_subtotal_price=833.33,
            original_total_price=833.33,
            # Subtotal changes, seems bad
            mapped_subtotal_price=694.44,
            mapped_total_price=833.33,
        )

    def test_price_excl_to_incl(self):
        """Test conversion of price from tax excl to tax incl.

        NB. as per Odoo standard behaviour, the subtotal of the price decreases.
        """
        self._test_price_conversion(
            self.tax_sale_excl,
            self.tax_sale_incl,
            product_price=833.33,
            original_subtotal_price=833.33,
            original_total_price=1000,
            # Subtotal changes, seems bad
            mapped_subtotal_price=694.44,
            mapped_total_price=833.33,
        )
