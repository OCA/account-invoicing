# Copyright (C) 2023-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from odoo.addons.stock_account.tests.test_account_move import TestAccountMoveStockCommon

from .tools import (
    create_with_form_product_product,
    create_with_form_stock_picking,
)


@tagged("post_install", "-at_install")
class TestStockPickingInvoicingCommon(TestAccountMoveStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Products Common Data
        cls.tax_model = cls.env["account.tax"]
        cls.tax_sale_1 = cls.tax_model.create(
            {"name": "Sale tax 20", "type_tax_use": "sale", "amount": "20.00"}
        )
        cls.tax_sale_2 = cls.tax_model.create(
            {"name": "Sale tax 10", "type_tax_use": "sale", "amount": "10.00"}
        )
        cls.tax_purchase_1 = cls.tax_model.create(
            {"name": "Purchase tax 10", "type_tax_use": "purchase", "amount": "10.00"}
        )
        cls.tax_purchase_2 = cls.tax_model.create(
            {"name": "Purchase tax 20", "type_tax_use": "purchase", "amount": "20.00"}
        )

        cls.account_revenue = cls.env["account.account"].search(
            [("account_type", "=", "expense_direct_cost")], limit=1
        )

        cls.common_product_values = {
            "lst_price": "15000",
            "taxes_id": cls.tax_sale_1 + cls.tax_sale_2,
            "supplier_taxes_id": cls.tax_purchase_1 + cls.tax_purchase_2,
            "property_account_income_id": cls.account_revenue,
            "standard_price": "500",
            "is_storable": True,
            "invoice_policy": "order",
        }

        # Products Storable
        cls.product_storable_1 = create_with_form_product_product(
            cls.env, cls.common_product_values | {"name": "Test 1", "type": "consu"}
        )
        cls.product_storable_2 = create_with_form_product_product(
            cls.env, cls.common_product_values | {"name": "Test 2", "type": "consu"}
        )

        # Fiscal Position
        fiscal_position = cls.env["account.fiscal.position"].create(
            {
                "name": "Test - Stock Picking Invoicing",
                "company_id": cls.company.id,
                "auto_apply": 1,
            }
        )
        cls.partner_a.property_account_position_id = fiscal_position

        # Common Picking Data
        cls.picking_type_out = cls.env["stock.picking.type"].search(
            [
                ("company_id", "=", cls.company.id),
                ("name", "=", "Delivery Orders"),
            ],
            limit=1,
        )

        picking_out_vals = {
            "partner_id": cls.partner_a,
            "picking_type_id": cls.picking_type_out,
        }

        cls.picking_type_in = cls.env["stock.picking.type"].search(
            [
                ("company_id", "=", cls.company.id),
                ("name", "=", "Receipts"),
            ],
            limit=1,
        )

        picking_in_vals = {
            "partner_id": cls.partner_a,
            "picking_type_id": cls.picking_type_in,
        }

        move_vals_1 = [
            {
                "product_id": cls.product_storable_1,
                "product_uom_qty": 1,
            }
        ]
        move_vals_2 = move_vals_1 + [
            {
                "product_id": cls.product_storable_2,
                "product_uom_qty": 1,
            }
        ]
        move_vals_3 = move_vals_1 + move_vals_2

        # Picking Out
        cls.picking_out_1 = create_with_form_stock_picking(
            cls.env, picking_out_vals, move_vals_1
        )
        cls.picking_out_2 = create_with_form_stock_picking(
            cls.env, picking_out_vals, move_vals_2
        )
        cls.picking_out_3 = create_with_form_stock_picking(
            cls.env, picking_out_vals, move_vals_3
        )

        # Picking In
        cls.picking_in_1 = create_with_form_stock_picking(
            cls.env, picking_in_vals, move_vals_1
        )

    def picking_move_state(self, picking):
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        with Form(picking) as picking_form:
            i = 0
            while i != len(picking.move_ids_without_package):
                with picking_form.move_ids_without_package.edit(i) as line:
                    line.quantity = line.product_uom_qty
                i += 1

            picking_form.save()
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def check_invoice_created(self, pickings, invoices):
        for picking in pickings:
            self.assertEqual(picking.invoice_state, "invoiced")
            for invoice in invoices:
                if picking.picking_type_id != self.picking_type_in:
                    # TODO: Invoice created by Picking Type In don't get user, why?
                    self.assertTrue(
                        invoice.invoice_user_id, "Error to map User in Invoice."
                    )

                self.assertIn(invoice.partner_id, pickings.mapped("partner_id"))
                self.assertIn(invoice, pickings.mapped("invoice_ids"))
                self.assertTrue(
                    invoice.invoice_payment_term_id,
                    "Error to map Payment Term in Invoice.",
                )
                self.assertTrue(
                    invoice.fiscal_position_id,
                    "Error to map Fiscal Position in Invoice.",
                )
                self.assertTrue(invoice.company_id, "Error to map Company in Invoice.")
                self.assertTrue(
                    invoice.invoice_line_ids, "Error to create invoice line."
                )

                for inv_line in invoice.invoice_line_ids:
                    self.assertTrue(inv_line.price_unit, "Error to get Price Unit")

                    self.assertTrue(
                        inv_line.product_uom_id,
                        "Error to map Product UOM in Invoice Line.",
                    )
                    self.assertIn(
                        inv_line.product_id,
                        [self.product_storable_1, self.product_storable_2],
                    )
                    self.assertTrue(
                        inv_line.tax_ids, "Error to map Tax in invoice.line."
                    )
                    for inv_mv_line in inv_line.move_line_ids:
                        link_pck_line = self.env["stock.move"].search(
                            [("id", "=", inv_mv_line.id)]
                        )
                        self.assertTrue(
                            link_pck_line,
                            "Error to link Invoice Line with Stock Move.",
                        )
