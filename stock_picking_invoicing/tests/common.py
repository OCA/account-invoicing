# Copyright (C) 2023-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.stock_account.tests.test_account_move import TestAccountMoveStockCommon

from .tools import (
    create_with_form_inv_onshipping,
    create_with_form_product_product,
    create_with_form_return_picking,
    create_with_form_stock_picking,
)


@tagged("post_install", "-at_install")
class TestStockPickingInvoicingCommon(TestAccountMoveStockCommon):
    # Force the generic chart template: the companies created by the test
    # framework (company_1_data, Branch A, ...) would otherwise guess their
    # chart template from their own country.
    chart_template = "generic_coa"

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

        # Partners
        cls.partner_stock_1 = cls.env["res.partner"].create(
            {
                "name": "Client 1 - stock_picking_invoicing",
                "country_id": cls.env.ref("base.be").id,
                "state_id": cls.env.ref("base.state_be_1").id,
                "street": "Rua A",
                "zip": "1234",
                "vat": "BE0477472701",
                "property_account_position_id": fiscal_position.id,
                "property_payment_term_id": cls.pay_terms_a.id,
                "property_supplier_payment_term_id": cls.pay_terms_a.id,
            }
        )

        # Common Picking Data
        cls.picking_type_out = cls.env["stock.picking.type"].search(
            [
                ("company_id", "=", cls.company.id),
                ("code", "=", "outgoing"),
            ],
            limit=1,
        )

        picking_out_vals = {
            "partner_id": cls.partner_stock_1,
            "picking_type_id": cls.picking_type_out,
        }

        cls.picking_type_in = cls.env["stock.picking.type"].search(
            [
                ("company_id", "=", cls.company.id),
                ("code", "=", "incoming"),
            ],
            limit=1,
        )

        picking_in_vals = {
            "partner_id": cls.partner_stock_1,
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

        # Picking Out
        cls.picking_out_1 = create_with_form_stock_picking(
            cls.env, picking_out_vals, move_vals_1
        )
        cls.picking_out_2 = create_with_form_stock_picking(
            cls.env, picking_out_vals, move_vals_2
        )

        # Picking In
        cls.picking_in_1 = create_with_form_stock_picking(
            cls.env, picking_in_vals, move_vals_1
        )

    def picking_move_state(self, picking):
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        for move in picking.move_ids_without_package:
            move.quantity = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def check_invoice_created(self, pickings, invoices):
        for picking in pickings:
            self.assertEqual(picking.invoice_state, "invoiced")
            for invoice in invoices:
                if invoice.move_type in ("out_invoice", "out_refund"):
                    # Only the Sale Invoices get a User: the Purchase Invoices
                    # created by the Wizard (in_invoice/in_refund, ex.: the
                    # Return to the Supplier) never do, no matter the type of
                    # the Picking they come from.
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
                    # The Price Unit can be 0.0 (free product, PriceList rule
                    # with price 0), so it can not be checked as a boolean:
                    # compare it with the price computed from the Stock Moves.
                    self.assertEqual(
                        inv_line.price_unit,
                        inv_line.move_line_ids._get_price_unit_invoice(
                            invoice.move_type,
                            invoice.partner_id,
                            inv_line.quantity,
                        ),
                        "Error to get Price Unit",
                    )

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

    def invoice_pickings(self, pickings, group="partner_product"):
        """Send the Picking(s) to the invoicing wizard.

        Check the Invoice(s) created and that no other Invoice was created
        by the wizard.
        """
        nb_invoice_before = self.env["account.move"].search_count([])
        invoices = create_with_form_inv_onshipping(self.env, pickings, group=group)
        self.check_invoice_created(pickings, invoices)
        self.assertEqual(
            nb_invoice_before,
            self.env["account.move"].search_count([]) - len(invoices),
            "No other Invoice should have been created.",
        )
        return invoices

    def _create_done_picking(self, picking_type):
        """Create a Picking with one Move and validate it (state done)."""
        picking = create_with_form_stock_picking(
            self.env,
            {"partner_id": self.partner_stock_1, "picking_type_id": picking_type},
            [{"product_id": self.product_storable_1, "product_uom_qty": 1}],
        )
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        return picking

    def _create_done_return(self, picking):
        """Create the Return of a done Picking and validate it."""
        return_picking = create_with_form_return_picking(self.env, picking)
        self.picking_move_state(return_picking)
        return_picking.set_to_be_invoiced()
        return return_picking

    def _invoice_mixed_pickings(self, pickings, inv_type):
        """Invoice the Pickings in ONE Wizard run and check the Invoice type.

        The type is decided by the FIRST Picking of the selection
        (`_get_invoice_type` reads `active_ids[0]`) and applied to every Invoice
        of the run, so a mixed selection of directions must end with all the
        Invoices of the same type.

        `create_with_form_inv_onshipping` is called directly (instead of the
        `invoice_pickings` helper) because the Invoice Type of the run is also
        checked here; `check_invoice_created` is called as well: with the
        Invoices of opposite directions it validates the User rule against the
        Invoice type (`move_type`) and not against the Picking type.
        """
        invoices = create_with_form_inv_onshipping(self.env, pickings)
        self.assertEqual([inv_type], list(set(invoices.mapped("move_type"))))
        self.check_invoice_created(pickings, invoices)
        return invoices

    def _invoice_line_of(self, invoices, picking):
        """Return the Invoice Line linked to the given Picking."""
        lines = invoices.invoice_line_ids.filtered(
            lambda line: line.move_line_ids.picking_id == picking
        )
        self.assertEqual(1, len(lines), "One Invoice Line per Picking expected.")
        return lines
