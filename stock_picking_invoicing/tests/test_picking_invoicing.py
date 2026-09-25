# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, exceptions
from odoo.tests import Form

from .common import TestStockPickingInvoicingCommon
from .tools import (
    create_with_form_inv_onshipping,
    create_with_form_pck_backorder,
    create_with_form_return_picking,
    create_with_form_stock_picking,
)


class TestStockPickingInvoicing(TestStockPickingInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_picking_out_invoicing(self):
        # Invoice the Picking Out of a Partner without PriceList (the Price
        # Unit to Invoice comes from the Product) and check the Invoice State
        # transitions done with the buttons before the Invoice creation
        self.partner_stock_1.write(
            {"type": "invoice", "property_product_pricelist": False}
        )
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
        self.invoice_pickings(picking)

    def test_02_picking_out_invoicing(self):
        # The Wizard must warn the user when there is nothing to invoice:
        # a validated Picking not marked as 'to be invoiced' (the message of
        # `action_generate` is checked with the Wizard built with the ORM)
        nb_invoice_before = self.env["account.move"].search_count([])
        picking = self.picking_out_2
        self.picking_move_state(picking)

        # Test Wizard Error
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

        # ... and also with an empty Picking selection, after the Picking has
        # been validated with the quantity informed by the user (the Picking
        # of the test is kept as 'none' invoice state as well)
        picking_not_invoiced = self.picking_out_1
        for line in picking_not_invoiced.move_ids_without_package:
            # Force Split
            line.quantity = 10

        picking_not_invoiced.button_validate()
        with self.assertRaises(exceptions.UserError):
            create_with_form_inv_onshipping(self.env, self.env["stock.picking"])

    def test_03_picking_out_invoicing(self):
        """
        Test invoicing picking in to check if get the taxes
        from supplier_taxes_id.
        """
        # Check the counting of pickings to be invoiced (used in kanban view)
        self.assertEqual(0, self.picking_type_in.count_picking_2binvoiced)
        picking = self.picking_in_1
        picking.set_to_be_invoiced()
        # Non stored computed field: force the recompute to read the new value
        self.picking_type_in.invalidate_recordset(["count_picking_2binvoiced"])
        self.assertEqual(1, self.picking_type_in.count_picking_2binvoiced)
        self.picking_move_state(picking)
        self.invoice_pickings(picking)

    def test_04_picking_out_invoicing_backorder(self):
        """
        Test invoicing picking out to check if backorder is create
        with same invoice state.
        """
        self.partner_stock_1.write({"type": "invoice"})
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

        invoice = self.invoice_pickings(picking)
        self.assertTrue(invoice.invoice_line_ids, "Error to create invoice line.")
        for inv_line in invoice.invoice_line_ids:
            # Test Price Unit informed by user
            self.assertEqual(
                inv_line.price_unit, 345.0, "Error in Price Unit informed by User."
            )

    def test_05_picking_cancel(self):
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

    def test_06_picking_invoice_refund(self):
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

    def test_07_picking_invoicing_by_product1(self):
        """
        Test the invoice generation grouped by partner/product with 1
        picking and 2 moves.
        :return:
        """
        self.partner_stock_1.write({"type": "invoice"})
        picking = self.picking_out_2
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        self.invoice_pickings(picking)

    def test_08_picking_invoicing_by_product2(self):
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

    def test_09_picking_invoicing_by_product3(self):
        """
        Test the invoice generation grouped by partner/product with 2
        picking and 2 moves per picking.
        We use different partner for 2 picking so we should have 2 invoice
        with 2 lines (and qty 1)
        :return:
        """
        # Check the case without PriceList
        self.env["product.pricelist"].search([]).unlink()

        picking_1 = self.picking_out_2
        picking_2 = picking_1.copy({"partner_id": self.partner_b.id})
        picking_1.set_to_be_invoiced()
        self.picking_move_state(picking_1)
        picking_2.set_to_be_invoiced()
        self.picking_move_state(picking_2)
        invoices = self.invoice_pickings(picking_1 | picking_2)
        self.assertEqual(len(invoices), 2)
        for invoice in invoices:
            self.assertEqual(len(invoice.picking_ids), 1)
            picking = invoice.picking_ids
            # Test the behaviour when the invoice is cancelled
            # The picking invoice_status should be updated
            invoice.button_cancel()
            self.assertEqual(picking.invoice_state, "2binvoiced")

    def test_10_return_customer_picking(self):
        """
        Test Return Customer Picking and Invoice created, and the Return
        Picking created with 'No invoicing', which must not be informed as
        'to be invoiced'.
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

        # Return Picking with 'No invoicing': the Return Picking must not be
        # informed as 'to be invoiced'
        picking_devolution_no_invoicing = create_with_form_return_picking(
            self.env, picking, invoice_state="none"
        )
        self.assertEqual(picking_devolution_no_invoicing.invoice_state, "none")
        for move in picking_devolution_no_invoicing.move_ids:
            self.assertEqual(move.invoice_state, "none")

    def test_11_return_supplier_picking(self):
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
                            "partner_id": self.partner_stock_1,
                            "min_qty": 1,
                            "price": 150,
                        }
                    )
                ]
            }
        )

        invoice = create_with_form_inv_onshipping(self.env, picking)
        for line in invoice.invoice_line_ids:
            seller = line.product_id.seller_ids.filtered(
                lambda seller: seller.partner_id == invoice.partner_id
            )
            self.assertEqual(
                len(seller),
                1,
                "Supplier Info of the Invoice Partner was not found.",
            )
            self.assertEqual(
                seller.price,
                line.price_unit,
                "Product Price in invoice line should " "be the same of Seller Price.",
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

    def test_12_get_price_from_pricelist(self):
        """Test get Price from PriceList.

        The Price Unit comes from the PriceList of the Partner, including the
        case of a PriceList rule with a fixed price of 0.0: the 0 informed by
        the PriceList must be kept on the Invoice Line, it must not fall back
        to another price (see `_simulate_invoice_line_onchange`).
        """
        price_list = self.env["product.pricelist"].create({"name": "Test pricelist"})
        price_list.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 1234.0,
                "applied_on": "0_product_variant",
                "product_id": self.product_storable_1.id,
                "pricelist_id": price_list.id,
            }
        )

        picking = self.picking_out_1
        picking.partner_id.property_product_pricelist = price_list
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        invoice = self.invoice_pickings(picking)
        self.assertEqual(picking.invoice_state, "invoiced")
        for inv_line in invoice.invoice_line_ids:
            if inv_line.product_id == self.product_storable_1:
                self.assertEqual(
                    inv_line.price_unit,
                    1234.0,
                    "Error to get sale Price from Price List.",
                )

        # Same case with a PriceList rule of 0: the 0 Price Unit must be kept
        # on the Invoice Line
        price_list_zero = self.env["product.pricelist"].create({"name": "PriceList 0"})
        price_list_zero.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 0.0,
                "applied_on": "0_product_variant",
                "product_id": self.product_storable_1.id,
                "pricelist_id": price_list_zero.id,
            }
        )
        picking_zero = create_with_form_stock_picking(
            self.env,
            {
                "partner_id": self.partner_stock_1,
                "picking_type_id": self.picking_type_out,
            },
            [{"product_id": self.product_storable_1, "product_uom_qty": 1}],
        )
        picking_zero.partner_id.property_product_pricelist = price_list_zero
        picking_zero.set_to_be_invoiced()
        self.picking_move_state(picking_zero)
        invoice_zero = self.invoice_pickings(picking_zero)
        self.assertEqual(picking_zero.invoice_state, "invoiced")
        self.assertEqual(0.0, invoice_zero.invoice_line_ids.price_unit)
        self.assertEqual(0.0, invoice_zero.amount_total)

    def test_13_picking_invoicing_group_by(self):
        """The 2 Grouping options of the Wizard, with the same Pickings.

        Grouping by Picking (default): one Invoice per Picking and one
        Invoice Line for each Stock Move (the Moves are not grouped by
        product). Grouping by Partner: one Invoice for all the Pickings of
        the Partner, still with one Invoice Line for each Stock Move (unlike
        the 'Partner/Product' grouping, the Moves of the same product are not
        merged in a single Invoice Line).
        """
        picking = self.picking_out_2
        picking2 = picking.copy()
        for pick in (picking, picking2):
            pick.set_to_be_invoiced()
            self.picking_move_state(pick)
        pickings = picking | picking2

        invoices = self.invoice_pickings(pickings, group="picking")
        self.assertEqual(len(invoices), 2)
        for invoice in invoices:
            self.assertEqual(len(invoice.picking_ids), 1)
            # 2 Stock Moves, so 2 Invoice Lines (no grouping by product)
            self.assertEqual(len(invoice.invoice_line_ids), 2)

        # Deleting the Invoices puts the Pickings back as 'to be invoiced'
        # (see the `unlink` override of `account.move`), so the same Pickings
        # can be sent to the Wizard again with the other Grouping option
        invoices.unlink()
        for pick in pickings:
            self.assertEqual(pick.invoice_state, "2binvoiced")

        invoice = self.invoice_pickings(pickings, group="partner")
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.picking_ids, pickings)
        # 2 Pickings with 2 Stock Moves each, so 4 Invoice Lines
        self.assertEqual(len(invoice.invoice_line_ids), 4)

    def test_14_picking_invoicing_other_company(self):
        """Pickings of another Company can not be invoiced."""
        other_company = self.branch_a["company"]
        picking_type = self.env["stock.picking.type"].search(
            [("company_id", "=", other_company.id), ("code", "=", "outgoing")],
            limit=1,
        )
        picking = create_with_form_stock_picking(
            self.env,
            {"partner_id": self.partner_stock_1, "picking_type_id": picking_type},
            [{"product_id": self.product_storable_1, "product_uom_qty": 1}],
        )
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        with self.assertRaises(exceptions.UserError) as e:
            create_with_form_inv_onshipping(self.env, picking)
        self.assertIn(
            "All pickings are not related to your company!", e.exception.args[0]
        )
        self.assertFalse(picking.invoice_ids, "Invoice should not be created.")

    def test_15_invoice_line_negative_quantity(self):
        """Negative quantity on the Invoice Line: mixed directions, one Invoice.

        The Invoice type is resolved ONCE per Wizard run, from the FIRST Picking
        of the selection (`_get_invoice_type` reads `active_ids[0]`), and applied
        to every Invoice; each Picking keeps the direction of its own Stock
        Moves. Invoicing together Pickings of opposite directions (a delivery
        and its return, a receipt and the return to the supplier), the Move that
        goes against the Invoice type has its quantity negated by
        `_get_invoice_line_values` (the sign rule by direction). Each block
        exercises one of the 4 branches.

        This is the real usage path: from the List view, select several Pickings
        and use the "Create Draft Invoices" action (bound to stock.picking). The
        ORDER matters: `active_ids[0]` is the first id of the recordset, so the
        Picking that decides the type must have the SMALLEST id of the pair.
        """
        # line 446: out_invoice + Move coming from the Customer (Delivery Return)
        delivery = self._create_done_picking(self.picking_type_out)
        customer_return = self._create_done_return(delivery)
        invoices = self._invoice_mixed_pickings(
            delivery | customer_return, "out_invoice"
        )
        self.assertEqual(1.0, self._invoice_line_of(invoices, delivery).quantity)
        self.assertEqual(
            -1.0, self._invoice_line_of(invoices, customer_return).quantity
        )

        # line 448: out_refund + Move going to the Customer (Delivery)
        other_delivery = self._create_done_picking(self.picking_type_out)
        first_return = self._create_done_return(other_delivery)
        compared_delivery = self._create_done_picking(self.picking_type_out)
        invoices = self._invoice_mixed_pickings(
            first_return | compared_delivery, "out_refund"
        )
        self.assertEqual(1.0, self._invoice_line_of(invoices, first_return).quantity)
        self.assertEqual(
            -1.0, self._invoice_line_of(invoices, compared_delivery).quantity
        )

        # line 450: in_invoice + Move going to the Supplier (Return to Supplier)
        receipt = self._create_done_picking(self.picking_type_in)
        vendor_return = self._create_done_return(receipt)
        invoices = self._invoice_mixed_pickings(receipt | vendor_return, "in_invoice")
        self.assertEqual(1.0, self._invoice_line_of(invoices, receipt).quantity)
        self.assertEqual(-1.0, self._invoice_line_of(invoices, vendor_return).quantity)

        # line 452: in_refund + Move coming from the Supplier (Receipt)
        other_receipt = self._create_done_picking(self.picking_type_in)
        first_vendor_return = self._create_done_return(other_receipt)
        compared_receipt = self._create_done_picking(self.picking_type_in)
        invoices = self._invoice_mixed_pickings(
            first_vendor_return | compared_receipt, "in_refund"
        )
        self.assertEqual(
            1.0, self._invoice_line_of(invoices, first_vendor_return).quantity
        )
        self.assertEqual(
            -1.0, self._invoice_line_of(invoices, compared_receipt).quantity
        )

    def test_16_form_stock_picking(self):
        """Test the Stock Picking and Stock Move forms (UI path).

        The done quantity of every Move is set through the picking form (as an
        user does in the web client) and then the picking is validated. It
        keeps the Form path of the picking/move covered, since the
        ``picking_move_state`` helper sets the done quantity directly on the
        moves.
        """
        picking = self.picking_out_2
        picking.action_confirm()
        picking.action_assign()
        with Form(picking) as picking_form:
            # Every Move of the Picking has to be filled: a Move left with
            # quantity 0 conflicts with its own demand and `button_validate`
            # returns the backorder wizard, so the Picking is not validated
            for index in range(len(picking.move_ids_without_package)):
                with picking_form.move_ids_without_package.edit(index) as line:
                    line.quantity = line.product_uom_qty
            picking_form.save()
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        # Every Move of the Picking was done with its own demand, set through
        # the Form
        self.assertEqual(picking.move_ids.mapped("quantity"), [1.0, 1.0])
