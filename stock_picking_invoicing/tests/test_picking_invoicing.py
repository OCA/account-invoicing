# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, exceptions

from .common import TestStockPickingInvoicingCommon
from .tools import (
    create_with_form_inv_onshipping,
    create_with_form_pck_backorder,
    create_with_form_return_picking,
)


class TestStockPickingInvoicing(TestStockPickingInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_picking_out_invoicing(self):
        nb_invoice_before = self.env["account.move"].search_count([])
        # Test case to Get Price Unit to Invoice when Partner don't has Pricelist
        self.partner_a.write({"type": "invoice", "property_product_pricelist": False})
        picking = self.picking_out_1
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(
            self.env,
            picking,
        )
        self.check_invoice_created(picking, invoice)
        nb_invoice_after = self.env["account.move"].search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))

    def test_02_picking_out_invoicing(self):
        nb_invoice_before = self.env["account.move"].search_count([])
        picking = self.picking_out_2
        self.picking_move_state(picking)

        # Test Wizard Error
        # invoice = create_with_form_inv_onshipping(
        #     self.env, picking,
        # )

        wizard_obj = self.env["stock.invoice.onshipping"].with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        with self.assertRaises(exceptions.UserError) as e:
            wizard.with_context(lang="en_US").action_generate()
        msg = "No invoice created!"
        self.assertIn(msg, e.exception.args[0])
        nb_invoice_after = self.env["account.move"].search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after)

    def test_03_picking_out_invoicing(self):
        nb_invoice_before = self.env["account.move"].search_count([])
        picking = self.picking_out_1
        picking.set_to_be_invoiced()

        # Test Set Not Invoice
        picking.set_as_not_billable()
        self.assertEqual(picking.invoice_state, "none")
        # Test Set Invoiced
        picking.set_as_invoiced()
        self.assertEqual(picking.invoice_state, "invoiced")

        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        self.check_invoice_created(picking, invoice)
        nb_invoice_after = self.env["account.move"].search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))

    def test_04_picking_out_invoicing(self):
        """
        Test invoicing picking in to check if get the taxes
        from supplier_taxes_id.
        """
        nb_invoice_before = self.env["account.move"].search_count([])
        picking = self.picking_in_1
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(
            self.env,
            picking,
        )
        self.check_invoice_created(picking, invoice)
        nb_invoice_after = self.env["account.move"].search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))

    def test_05_picking_out_invoicing_backorder(self):
        """
        Test invoicing picking out to check if backorder is create
        with same invoice state.
        """
        nb_invoice_before = self.env["account.move"].search_count([])
        self.partner_a.write({"type": "invoice"})
        picking = self.picking_out_1
        picking.set_to_be_invoiced()
        # Test BackOrder need to open Wizard
        # self.picking_move_state(picking)
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity = move.product_uom_qty / 2.0
            # Test Price Unit informed by User
            move.price_unit = 345.0

        backorder = create_with_form_pck_backorder(self.env, picking)
        backorder.action_assign()
        self.assertEqual(backorder.invoice_state, "2binvoiced")
        self.assertEqual(picking.state, "done")

        invoice = create_with_form_inv_onshipping(self.env, picking)
        self.check_invoice_created(picking, invoice)
        nb_invoice_after = self.env["account.move"].search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))
        self.assertTrue(invoice.invoice_line_ids, "Error to create invoice line.")
        for inv_line in invoice.invoice_line_ids:
            # Test Price Unit informed by user
            self.assertEqual(
                inv_line.price_unit, 345.0, "Error in Price Unit informed by User."
            )

    def test_06_picking_cancel(self):
        """
        Ensure that the invoice_state of the picking is correctly
        updated when an invoice is cancelled
        :return:
        """
        nb_invoice_before = self.env["account.move"].search_count([])
        picking = self.picking_out_1
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        self.check_invoice_created(picking, invoice)
        invoice.button_cancel()
        self.assertEqual(picking.invoice_state, "2binvoiced")
        invoice.button_draft()
        self.assertEqual(picking.invoice_state, "invoiced")
        self.check_invoice_created(picking, invoice)
        nb_invoice_after = self.env["account.move"].search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))

    def test_07_picking_invoice_refund(self):
        """
        Ensure that a refund keep the link to the picking
        :return:
        """
        nb_invoice_before = self.env["account.move"].search_count([])
        picking = self.picking_out_1
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        self.check_invoice_created(picking, invoice)
        invoice.action_post()
        refund = invoice._reverse_moves(cancel=True)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertIn(picking, refund.picking_ids)
        nb_invoice_after = self.env["account.move"].search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice | refund))

    def test_08_picking_invoicing_by_product1(self):
        """
        Test the invoice generation grouped by partner/product with 1
        picking and 2 moves.
        :return:
        """
        nb_invoice_before = self.env["account.move"].search_count([])
        self.partner.write({"type": "invoice"})
        picking = self.picking_out_2
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        self.check_invoice_created(picking, invoice)
        nb_invoice_after = self.env["account.move"].search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))

    def test_09_picking_invoicing_by_product2(self):
        """
        Test the invoice generation grouped by partner/product with 2
        picking and 2 moves per picking.
        We use same partner for 2 picking so we should have 1 invoice with 2
        lines (and qty 2)
        :return:
        """
        nb_invoice_before = self.env["account.move"].search_count([])
        picking = self.picking_out_2
        picking2 = picking.copy()
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        picking2.set_to_be_invoiced()
        self.picking_move_state(picking2)
        pickings = picking | picking2
        invoice = create_with_form_inv_onshipping(self.env, pickings)
        self.check_invoice_created(pickings, invoice)
        for inv_line in invoice.invoice_line_ids:
            self.assertAlmostEqual(inv_line.quantity, 2)
        # Now test behaviour if the invoice is delete
        invoice.unlink()
        for picking in pickings:
            self.assertEqual(picking.invoice_state, "2binvoiced")
        nb_invoice_after = self.env["account.move"].search_count([])
        # Should be equals because we delete the invoice
        self.assertEqual(nb_invoice_before, nb_invoice_after)

    def test_10_picking_invoicing_by_product3(self):
        """
        Test the invoice generation grouped by partner/product with 2
        picking and 2 moves per picking.
        We use different partner for 2 picking so we should have 2 invoice
        with 2 lines (and qty 1)
        :return:
        """
        # Check the case without PriceList
        self.env["product.pricelist"].search([]).unlink()

        nb_invoice_before = self.env["account.move"].search_count([])
        picking = self.picking_out_2
        picking2 = picking.copy({"partner_id": self.partner_b.id})
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        picking2.set_to_be_invoiced()
        self.picking_move_state(picking2)
        pickings = picking | picking2
        invoices = create_with_form_inv_onshipping(self.env, pickings)
        self.assertEqual(len(invoices), 2)
        self.check_invoice_created(pickings, invoices)
        for invoice in invoices:
            self.assertEqual(len(invoice.picking_ids), 1)
            picking = invoice.picking_ids
            # Test the behaviour when the invoice is cancelled
            # The picking invoice_status should be updated
            invoice.button_cancel()
            self.assertEqual(picking.invoice_state, "2binvoiced")
        nb_invoice_after = self.env["account.move"].search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoices))

    def test_11_counting_2binvoiced(self):
        """
        Check method counting 2binvoice used in kanban view
        """
        self.assertEqual(0, self.picking_type_in.count_picking_2binvoiced)

    def test_12_return_customer_picking(self):
        """
        Test Return Customer Picking and Invoice created.
        """
        picking = self.picking_out_1
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        # Confirm Invoice
        invoice.action_post()
        self.assertEqual(invoice.state, "posted", "Invoice should be in state Posted")
        # Check Invoice Type
        self.assertEqual(
            invoice.move_type, "out_invoice", "Invoice Type should be Out Invoice"
        )

        # Return Picking
        picking_devolution = create_with_form_return_picking(self.env, picking)

        self.assertEqual(picking_devolution.invoice_state, "2binvoiced")
        for line in picking_devolution.move_ids:
            self.assertEqual(line.invoice_state, "2binvoiced")

        self.picking_move_state(picking_devolution)
        invoice_devolution = create_with_form_inv_onshipping(
            self.env, picking_devolution
        )
        self.check_invoice_created(picking_devolution, invoice_devolution)
        # Confirm Return Invoice
        invoice_devolution.action_post()
        self.assertEqual(
            invoice_devolution.state, "posted", "Invoice should be in state Posted"
        )
        # Check Invoice Type
        self.assertEqual(
            invoice_devolution.move_type,
            "out_refund",
            "Invoice Type should be Out Refund",
        )

    def test_13_return_supplier_picking(self):
        """
        Test Return Supplier Picking and Invoice created.
        """
        picking = self.picking_in_1
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)

        self.product_storable_1.write(
            {
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": self.partner_a,
                            "min_qty": 1,
                            "price": 150,
                        }
                    )
                ]
            }
        )

        invoice = create_with_form_inv_onshipping(self.env, picking)
        for line in invoice.invoice_line_ids:
            for seller in line.product_id.seller_ids:
                if seller.partner_id == invoice.partner_id:
                    self.assertEqual(
                        seller.price,
                        line.price_unit,
                        "Product Price in invoice line should "
                        "be the same of Seller Price.",
                    )
        # Confirm Invoice
        invoice.action_post()
        self.assertEqual(invoice.state, "posted", "Invoice should be in state Posted")
        # Check Invoice Type
        self.assertEqual(
            invoice.move_type, "in_invoice", "Invoice Type should be In Invoice"
        )

        # Return Picking
        picking_devolution = create_with_form_return_picking(self.env, picking)

        self.assertEqual(picking_devolution.invoice_state, "2binvoiced")
        for line in picking_devolution.move_ids:
            self.assertEqual(line.invoice_state, "2binvoiced")

        self.picking_move_state(picking_devolution)
        invoice_devolution = create_with_form_inv_onshipping(
            self.env, picking_devolution
        )
        # Confirm Return Invoice
        invoice_devolution.action_post()
        self.assertEqual(
            invoice_devolution.state, "posted", "Invoice should be in state Posted"
        )
        # Check Invoice Type
        self.assertEqual(
            invoice_devolution.move_type,
            "in_refund",
            "Invoice Type should be In Refund",
        )

    def test_14_get_price_from_pricelist(self):
        """Test get Price from PriceList."""

        price_list = self.env["product.pricelist"].create({"name": "Test pricelist"})
        price_list.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 1234.0,
                "applied_on": "0_product_variant",
                "product_id": self.product_storable_1.id,  # product_price_test.id,
                "pricelist_id": price_list.id,
            }
        )

        picking = self.picking_out_1
        picking.partner_id.property_product_pricelist = price_list
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        self.check_invoice_created(picking, invoice)
        self.assertEqual(picking.invoice_state, "invoiced")
        for inv_line in invoice.invoice_line_ids:
            if inv_line.product_id == self.product_storable_1:
                self.assertEqual(
                    inv_line.price_unit,
                    1234.0,
                    "Error to get sale Price from Price List.",
                )

    def test_15_picking_extra_vals(self):
        """Test Picking Extra Vals"""
        picking = self.picking_out_1

        for line in picking.move_ids_without_package:
            # Force Split
            line.quantity = 10

        picking.button_validate()
        with self.assertRaises(exceptions.UserError):
            create_with_form_inv_onshipping(self.env, self.env["stock.picking"])
