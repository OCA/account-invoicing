# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo import exceptions

from .common import TestPickingInvoicingCommon


class TestPickingInvoicing(TestPickingInvoicingCommon):
    def test_01_picking_out_invoicing(self):
        # setting Agrolait type to default, because it's 'contact' in demo data
        nb_invoice_before = self.invoice_model.search_count([])
        # Test case to Get Price Unit to Invoice when Partner don't has Pricelist
        self.partner.write({"type": "invoice", "property_product_pricelist": False})
        picking = self.picking_model.create(
            {
                "partner_id": self.partner2.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        move_vals = {
            "product_id": self.product_test_1.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 2,
            "uom_id": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")
        invoice = self.create_invoice_wizard(picking)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))
        assert invoice.invoice_user_id, "Error to map User in Invoice."
        assert invoice.invoice_payment_term_id, "Error to map Payment Term in Invoice."
        assert invoice.fiscal_position_id, "Error to map Fiscal Position in Invoice."
        assert invoice.company_id, "Error to map Company in Invoice."
        assert invoice.invoice_line_ids, "Error to create invoice line."
        for inv_line in invoice.invoice_line_ids:
            assert inv_line.account_id, "Error to map Account in Invoice Line."
            assert inv_line.tax_ids, "Error to map Sale Tax in Invoice Line."
            assert inv_line.product_uom_id, "Error to map Product UOM in Invoice Line."
            assert inv_line.price_unit, "Error in Price Unit"
            assert inv_line.move_line_ids, (
                "Error, there no relation between Invoice Line and Stock Move Line."
            )
            for mv_line in inv_line.move_line_ids:
                self.assertEqual(
                    mv_line.id,
                    new_move.id,
                    "Error to link stock.move with invoice.line.",
                )

    def test_02_picking_out_invoicing(self):
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({"type": "invoice"})
        picking = self.picking_model.create(
            {
                "partner_id": self.partner2.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        move_vals = {
            "product_id": self.product_test_1.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 2,
            "uom_id": self.product_test_1.uom_id.id,
        }
        self.move_model.create(move_vals)
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")

        # Test Wizard Error
        # self.create_invoice_wizard(picking)
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
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after)

    def test_03_picking_out_invoicing(self):
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({"type": "invoice"})
        picking = self.picking_model.create(
            {
                "partner_id": self.partner2.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        move_vals = {
            "product_id": self.product_test_1.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 2,
            "uom_id": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        picking.set_to_be_invoiced()

        # Test Set Not Invoice
        picking.set_as_not_billable()
        self.assertEqual(picking.invoice_state, "none")
        # Test Set Invoiced
        picking.set_as_invoiced()
        self.assertEqual(picking.invoice_state, "invoiced")

        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")
        invoice = self.create_invoice_wizard(picking)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))
        assert invoice.invoice_line_ids, "Error to create invoice line."
        for inv_line in invoice.invoice_line_ids:
            for mv_line in inv_line.move_line_ids:
                self.assertEqual(
                    mv_line.id,
                    new_move.id,
                    "Error to link stock.move with invoice.line.",
                )
            self.assertTrue(inv_line.tax_ids, "Error to map Sale Tax in invoice.line.")

    def test_04_picking_out_invoicing(self):
        """
        Test invoicing picking in to check if get the taxes
        from supplier_taxes_id.
        """
        nb_invoice_before = self.invoice_model.search_count([])
        picking = self.picking_model.create(
            {
                "partner_id": self.supplier.id,
                "picking_type_id": self.pick_type_in.id,
                "location_id": self.suppliers_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move_vals = {
            "product_id": self.product_test_1.id,
            "picking_id": picking.id,
            "location_dest_id": self.stock_location.id,
            "location_id": self.suppliers_location.id,
            "product_uom_qty": 2,
            "uom_id": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")
        invoice = self.create_invoice_wizard(picking)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(invoice.partner_id, self.supplier)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))
        assert invoice.invoice_line_ids, "Error to create invoice line."
        for inv_line in invoice.invoice_line_ids:
            for mv_line in inv_line.move_line_ids:
                self.assertEqual(
                    mv_line.id,
                    new_move.id,
                    "Error to link stock.move with invoice.line.",
                )
            self.assertTrue(
                inv_line.tax_ids,
                "Error to map Purchase Tax in invoice.line.",
            )

    def test_05_picking_out_invoicing_backorder(self):
        """
        Test invoicing picking out to check if backorder is create
        with same invoice state.
        """
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({"type": "invoice"})
        picking = self.picking_model.create(
            {
                "partner_id": self.partner2.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        move_vals = {
            "product_id": self.product_test_1.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 4,
            "uom_id": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        picking.set_to_be_invoiced()
        # Test BackOrder need to open Wizard
        # self.picking_move_state(picking)
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty / 2.0
            # Test Price Unit informed by User
            move.price_unit = 345.0

        backorder = self.create_backorder_wizard(picking)
        backorder.action_assign()
        self.assertEqual(backorder.invoice_state, "2binvoiced")

        self.assertEqual(picking.state, "done")
        invoice = self.create_invoice_wizard(picking)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))
        assert invoice.invoice_line_ids, "Error to create invoice line."
        for inv_line in invoice.invoice_line_ids:
            for mv_line in inv_line.move_line_ids:
                self.assertEqual(
                    mv_line.id,
                    new_move.id,
                    "Error to link stock.move with invoice.line.",
                )
            self.assertTrue(inv_line.tax_ids, "Error to map Sale Tax in invoice.line.")
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
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({"type": "invoice"})
        picking = self.picking_model.create(
            {
                "partner_id": self.partner2.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        move_vals = {
            "product_id": self.product_test_1.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 2,
            "uom_id": self.product_test_1.uom_id.id,
        }
        self.move_model.create(move_vals)
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")
        invoice = self.create_invoice_wizard(picking)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(invoice.partner_id, self.partner)
        invoice.button_cancel()
        self.assertEqual(picking.invoice_state, "2binvoiced")
        invoice.button_draft()
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))

    def test_07_picking_invoice_refund(self):
        """
        Ensure that a refund keep the link to the picking
        :return:
        """
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({"type": "invoice"})
        picking = self.picking_model.create(
            {
                "partner_id": self.partner2.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        move_vals = {
            "product_id": self.product_test_1.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 2,
            "uom_id": self.product_test_1.uom_id.id,
        }
        self.move_model.create(move_vals)
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")
        invoice = self.create_invoice_wizard(picking)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        invoice.action_post()
        refund = invoice._reverse_moves(cancel=True)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertIn(picking, refund.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice | refund))

    def test_08_picking_invoicing_by_product1(self):
        """
        Test the invoice generation grouped by partner/product with 1
        picking and 2 moves.
        :return:
        """
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({"type": "invoice"})
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        move_vals = {
            "product_id": self.product_test_1.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 1,
            "uom_id": self.product_test_1.uom_id.id,
        }
        self.move_model.create(move_vals)
        move_vals2 = {
            "product_id": self.product_test_2.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 1,
            "uom_id": self.product_test_2.uom_id.id,
        }
        self.move_model.create(move_vals2)
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")
        invoice = self.create_invoice_wizard(picking)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        products = invoice.invoice_line_ids.mapped("product_id")
        self.assertEqual(len(invoice.invoice_line_ids), 2)
        self.assertIn(self.product_test_1, products)
        self.assertIn(self.product_test_2, products)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoice))

    def test_09_picking_invoicing_by_product2(self):
        """
        Test the invoice generation grouped by partner/product with 2
        picking and 2 moves per picking.
        We use same partner for 2 picking so we should have 1 invoice with 2
        lines (and qty 2)
        :return:
        """
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({"type": "invoice"})
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        move_vals = {
            "product_id": self.product_test_1.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 1,
            "uom_id": self.product_test_1.uom_id.id,
        }
        self.move_model.create(move_vals)
        picking2 = picking.copy()
        move_vals2 = {
            "product_id": self.product_test_1.id,
            "picking_id": picking2.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 1,
            "uom_id": self.product_test_1.uom_id.id,
        }
        self.move_model.create(move_vals2)
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        picking2.set_to_be_invoiced()
        self.picking_move_state(picking2)
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking2.state, "done")
        pickings = picking | picking2
        invoice = self.create_invoice_wizard(pickings)
        self.assertEqual(len(invoice), 1)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(picking2.invoice_state, "invoiced")
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(invoice, picking2.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        self.assertIn(picking2, invoice.picking_ids)
        products = invoice.invoice_line_ids.mapped("product_id")
        self.assertIn(self.product_test_1, products)
        for inv_line in invoice.invoice_line_ids:
            # qty = 3 because 1 move + duplicate one + 1 new
            self.assertAlmostEqual(inv_line.quantity, 3)
            self.assertTrue(inv_line.tax_ids, "Error to map Sale Tax in invoice.line.")
        # Now test behaviour if the invoice is delete
        invoice.unlink()
        for picking in pickings:
            self.assertEqual(picking.invoice_state, "2binvoiced")
        nb_invoice_after = self.invoice_model.search_count([])
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
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({"type": "invoice"})
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        move_vals = {
            "product_id": self.product_test_1.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 1,
            "uom_id": self.product_test_1.uom_id.id,
        }
        self.move_model.create(move_vals)
        picking2 = picking.copy({"partner_id": self.partner3.id})
        move_vals2 = {
            "product_id": self.product_test_2.id,
            "picking_id": picking2.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "product_uom_qty": 1,
            "uom_id": self.product_test_2.uom_id.id,
        }
        self.move_model.create(move_vals2)
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)

        picking2.set_to_be_invoiced()
        self.picking_move_state(picking2)
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking2.state, "done")
        pickings = picking | picking2
        invoices = self.create_invoice_wizard(pickings)

        self.assertEqual(len(invoices), 2)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(picking2.invoice_state, "invoiced")
        self.assertIn(self.partner, invoices.mapped("partner_id"))
        self.assertIn(self.partner3, invoices.mapped("partner_id"))
        for invoice in invoices:
            self.assertEqual(len(invoice.picking_ids), 1)
            picking = invoice.picking_ids
            self.assertIn(invoice, picking.invoice_ids)
            for inv_line in invoice.invoice_line_ids:
                self.assertAlmostEqual(inv_line.quantity, 1)
                self.assertTrue(
                    inv_line.tax_ids,
                    "Error to map Sale Tax in invoice.line.",
                )
            # Test the behaviour when the invoice is cancelled
            # The picking invoice_status should be updated
            invoice.button_cancel()
            self.assertEqual(picking.invoice_state, "2binvoiced")
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after - len(invoices))

    def test_11_counting_2binvoiced(self):
        """
        Check method counting 2binvoice used in kanban view
        """
        self.assertEqual(1, self.pick_type_in.count_picking_2binvoiced)

    def test_12_return_customer_picking(self):
        """
        Test Return Customer Picking and Invoice created.
        """
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "invoice_state": "2binvoiced",
                "origin": "stock_picking_invoicing demo",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_price_test.id,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
                "product_uom_qty": 2,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")
        invoice = self.create_invoice_wizard(picking)
        # Confirm Invoice
        invoice.action_post()
        self.assertEqual(invoice.state, "posted", "Invoice should be in state Posted")
        # Check Invoice Type
        self.assertEqual(
            invoice.move_type, "out_invoice", "Invoice Type should be Out Invoice"
        )

        # Return Picking
        picking_devolution = self.return_picking_wizard(picking)

        self.assertEqual(picking_devolution.invoice_state, "2binvoiced")
        for line in picking_devolution.move_ids:
            self.assertEqual(line.invoice_state, "2binvoiced")

        self.picking_move_state(picking_devolution)
        self.assertEqual(picking_devolution.state, "done", "Change state fail.")
        invoice_devolution = self.create_invoice_wizard(picking_devolution)
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
        self.assertEqual(invoice_devolution.invoice_line_ids.quantity, 1)

    def test_13_return_supplier_picking(self):
        """
        Test Return Supplier Picking and Invoice created.
        """
        picking = self.picking_model.create(
            {
                "partner_id": self.partner4.id,
                "picking_type_id": self.pick_type_in.id,
                "invoice_state": "2binvoiced",
                "origin": "stock_picking_invoicing demo",
                "location_id": self.suppliers_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_price_test.id,
                "picking_id": picking.id,
                "location_id": self.suppliers_location.id,
                "location_dest_id": self.stock_location.id,
                "product_uom_qty": 2,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner4.id,
                "product_id": self.product_price_test.id,
                "price": 800.0,
            }
        )
        invoice = self.create_invoice_wizard(picking)
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
        picking_devolution = self.return_picking_wizard(picking)

        self.assertEqual(picking_devolution.invoice_state, "2binvoiced")
        for line in picking_devolution.move_ids:
            self.assertEqual(line.invoice_state, "2binvoiced")

        self.picking_move_state(picking_devolution)
        self.assertEqual(picking_devolution.state, "done", "Change state fail.")

        invoice_devolution = self.create_invoice_wizard(picking_devolution)
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
        self.assertEqual(invoice_devolution.invoice_line_ids.quantity, 1)

    def test_14_get_price_from_pricelist(self):
        """Test get Price from PriceList."""
        self.partner.write(
            {"type": "invoice", "property_product_pricelist": self.price_list.id}
        )
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "invoice_state": "2binvoiced",
                "origin": "stock_picking_invoicing demo",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_price_test.id,
                "product_uom_qty": 1,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
                "uom_id": self.product_price_test.uom_id.id,
            }
        )
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")
        invoice = self.create_invoice_wizard(picking)
        self.assertEqual(picking.invoice_state, "invoiced")
        for inv_line in invoice.invoice_line_ids:
            if inv_line.product_id == self.product_price_test:
                self.assertEqual(
                    inv_line.price_unit,
                    1234.0,
                    "Error to get sale Price from Price List.",
                )

    def test_15_picking_extra_vals(self):
        """Test Picking Extra Vals"""
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "invoice_state": "2binvoiced",
                "origin": "stock_picking_invoicing demo",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_test_1.id,
                "product_uom_qty": 1,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
                "uom_id": self.product_test_1.uom_id.id,
            }
        )

        self._run_picking_onchanges(picking)

        for line in picking.move_ids:
            # Force Split
            line.quantity = 10

        picking.button_validate()

    def test_16_return_none_is_not_invoiced(self):
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "invoice_state": "2binvoiced",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_test_1.id,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
                "product_uom_qty": 2,
                "uom_id": self.product_test_1.uom_id.id,
            }
        )
        self.picking_move_state(picking)
        self.create_invoice_wizard(picking).action_post()
        picking_devolution = self.return_picking_wizard(picking, invoice_state="none")
        self.assertEqual(picking_devolution.invoice_state, "none")
        self.picking_move_state(picking_devolution)
        wizard_obj = self.env["stock.invoice.onshipping"].with_context(
            active_ids=picking_devolution.ids,
            active_model=picking_devolution._name,
            active_id=picking_devolution.id,
        )
        wizard = wizard_obj.create(
            wizard_obj.default_get(wizard_obj.fields_get().keys())
        )
        with self.assertRaises(exceptions.UserError):
            wizard.action_generate()

    def test_17_purchase_seller_uom_price(self):
        dozen = self.env.ref("uom.product_uom_dozen")
        seller = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_id": self.product_test_1.id,
                "price": 24.0,
                "uom_id": dozen.id,
            }
        )
        picking = self.picking_model.create(
            {
                "partner_id": self.supplier.id,
                "picking_type_id": self.pick_type_in.id,
                "invoice_state": "2binvoiced",
                "location_id": self.suppliers_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_test_1.id,
                "picking_id": picking.id,
                "location_id": self.suppliers_location.id,
                "location_dest_id": self.stock_location.id,
                "product_uom_qty": 1,
                "uom_id": self.product_test_1.uom_id.id,
            }
        )
        self.picking_move_state(picking)
        invoice = self.create_invoice_wizard(picking)
        expected_price = seller.uom_id._compute_price(24.0, self.product_test_1.uom_id)
        invoice_line = invoice.invoice_line_ids
        self.assertEqual(invoice.move_type, "in_invoice")
        self.assertAlmostEqual(invoice_line.price_unit, expected_price)
        self.assertTrue(invoice_line.account_id)

    def test_18_journal_type_without_moves(self):
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        journal_type = (
            self.env["stock.invoice.onshipping"]
            .with_context(active_ids=picking.ids)
            ._get_journal_type()
        )
        self.assertEqual(journal_type, "sale")

    def test_19_customer_origin_flips_quantity(self):
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "invoice_state": "2binvoiced",
                "location_id": self.customers_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_test_1.id,
                "picking_id": picking.id,
                "location_id": self.customers_location.id,
                "location_dest_id": self.stock_location.id,
                "product_uom_qty": 1,
                "uom_id": self.product_test_1.uom_id.id,
            }
        )
        self.picking_move_state(picking)
        invoice = self.create_invoice_wizard(picking)
        self.assertEqual(invoice.invoice_line_ids.quantity, -1)

    def test_20_generate_when_action_has_no_views(self):
        picking = self.picking_model.create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.pick_type_out.id,
                "invoice_state": "2binvoiced",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
            }
        )
        self.move_model.create(
            {
                "product_id": self.product_test_1.id,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customers_location.id,
                "product_uom_qty": 1,
                "uom_id": self.product_test_1.uom_id.id,
            }
        )
        self.picking_move_state(picking)
        wizard = self.env["stock.invoice.onshipping"].with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        wizard = wizard.create(wizard.default_get(wizard.fields_get().keys()))
        action_model = type(self.env["ir.actions.act_window"])
        with patch.object(
            action_model,
            "_for_xml_id",
            return_value={"type": "ir.actions.act_window", "res_model": "account.move"},
        ):
            action = wizard.action_generate()
        self.assertEqual(
            action["views"],
            [(self.env.ref("account.view_move_form").id, "form")],
        )
        self.assertTrue(action["res_id"])

    def test_21_other_company_picking_is_rejected(self):
        company = self.env["res.company"].create({"name": "Coverage Co"})
        warehouse = (
            self.env["stock.warehouse"]
            .with_company(company)
            .create(
                {
                    "name": "Coverage",
                    "code": "COV",
                    "company_id": company.id,
                }
            )
        )
        picking = (
            self.env["stock.picking"]
            .with_company(company)
            .create(
                {
                    "partner_id": self.partner.id,
                    "picking_type_id": warehouse.out_type_id.id,
                    "location_id": warehouse.lot_stock_id.id,
                    "location_dest_id": self.customers_location.id,
                    "invoice_state": "2binvoiced",
                }
            )
        )
        wizard = self.env["stock.invoice.onshipping"].with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        wizard = wizard.create(wizard.default_get(wizard.fields_get().keys()))
        with self.assertRaises(exceptions.UserError):
            wizard.action_generate()
