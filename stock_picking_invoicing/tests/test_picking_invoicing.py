# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo import fields, exceptions


class TestPickingInvoicing(TransactionCase):

    def setUp(self):
        super(TestPickingInvoicing, self).setUp()
        self.picking_model = self.env['stock.picking']
        self.move_model = self.env['stock.move']
        self.invoice_wizard = self.env['stock.invoice.onshipping']
        self.invoice_model = self.env['account.invoice']
        self.partner_model = self.env['res.partner']
        self.partner = self.env.ref('base.res_partner_2')
        self.partner2 = self.env.ref('base.res_partner_address_4')
        self.partner3 = self.env.ref('base.res_partner_18')
        self.pick_type_in = self.env.ref("stock.picking_type_in")
        self.location = self.env.ref("stock.stock_location_stock")
        self.location_dest = self.env.ref("stock.stock_location_customers")
        self.product = self.env.ref("product.product_product_10")
        self.product2 = self.env.ref("product.product_product_11")
        self.journal = self.env['account.journal'].create({
            'name': 'A super journal name',
            'code': 'ABC',
            'type': 'sale',
            'refund_sequence': True,
        })

    def test_0_picking_invoicing(self):
        # setting Agrolait type to default, because it's 'contact' in demo data
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({'type': 'invoice'})
        picking = self.picking_model.create({
            'partner_id': self.partner2.id,
            'picking_type_id': self.pick_type_in.id,
            'location_id': self.location.id,
            'location_dest_id': self.location_dest.id,
        })
        move_vals = {
            'product_id': self.product.id,
            'picking_id': picking.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product.name,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move.onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, 'done')
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        action = wizard.action_generate()
        domain = action.get('domain', [])
        invoice = self.invoice_model.search(domain)
        self.assertEqual(picking.invoice_state, 'invoiced')
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEquals(nb_invoice_before, nb_invoice_after - len(invoice))
        assert invoice.invoice_line_ids, 'Error to create invoice line.'
        for inv_line in invoice.invoice_line_ids:
            for mv_line in inv_line.move_line_ids:
                self.assertEquals(
                    mv_line.id, new_move.id,
                    'Error to link stock.move with invoice.line.')

    def test_1_picking_invoicing(self):
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({'type': 'invoice'})
        picking = self.picking_model.create({
            'partner_id': self.partner2.id,
            'picking_type_id': self.pick_type_in.id,
            'location_id': self.location.id,
            'location_dest_id': self.location_dest.id,
        })
        move_vals = {
            'product_id': self.product.id,
            'picking_id': picking.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product.name,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move.onchange_product_id()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, 'done')
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        with self.assertRaises(exceptions.UserError) as e:
            wizard.action_generate()
        msg = "No invoice created!"
        self.assertIn(msg, e.exception.name)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEquals(nb_invoice_before, nb_invoice_after)

    def test_2_picking_invoicing(self):
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({'type': 'invoice'})
        picking = self.picking_model.create({
            'partner_id': self.partner2.id,
            'picking_type_id': self.pick_type_in.id,
            'location_id': self.location.id,
            'location_dest_id': self.location_dest.id,
        })
        move_vals = {
            'product_id': self.product.id,
            'picking_id': picking.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product.name,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move.onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, 'done')
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard_values.update({
            'group': 'partner',
        })
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        action = wizard.action_generate()
        domain = action.get('domain', [])
        invoice = self.invoice_model.search(domain)
        self.assertEqual(picking.invoice_state, 'invoiced')
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEquals(nb_invoice_before, nb_invoice_after - len(invoice))
        assert invoice.invoice_line_ids, 'Error to create invoice line.'
        for inv_line in invoice.invoice_line_ids:
            for mv_line in inv_line.move_line_ids:
                self.assertEquals(
                    mv_line.id, new_move.id,
                    'Error to link stock.move with invoice.line.')

    def test_picking_cancel(self):
        """
        Ensure that the invoice_state of the picking is correctly
        updated when an invoice is cancelled
        :return:
        """
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({'type': 'invoice'})
        picking = self.picking_model.create({
            'partner_id': self.partner2.id,
            'picking_type_id': self.pick_type_in.id,
            'location_id': self.location.id,
            'location_dest_id': self.location_dest.id,
        })
        move_vals = {
            'product_id': self.product.id,
            'picking_id': picking.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product.name,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move.onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, 'done')
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard_values.update({
            'group': 'partner',
        })
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        action = wizard.action_generate()
        domain = action.get('domain', [])
        invoice = self.invoice_model.search(domain)
        self.assertEqual(picking.invoice_state, 'invoiced')
        self.assertEqual(invoice.partner_id, self.partner)
        invoice.action_cancel()
        self.assertEqual(picking.invoice_state, '2binvoiced')
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEquals(nb_invoice_before, nb_invoice_after - len(invoice))

    def test_picking_invoice_refund(self):
        """
        Ensure that a refund keep the link to the picking
        :return:
        """
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({'type': 'invoice'})
        picking = self.picking_model.create({
            'partner_id': self.partner2.id,
            'picking_type_id': self.pick_type_in.id,
            'location_id': self.location.id,
            'location_dest_id': self.location_dest.id,
        })
        move_vals = {
            'product_id': self.product.id,
            'picking_id': picking.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product.name,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move.onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, 'done')
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard_values.update({
            'group': 'partner',
        })
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        action = wizard.action_generate()
        domain = action.get('domain', [])
        invoice = self.invoice_model.search(domain)
        self.assertEqual(picking.invoice_state, 'invoiced')
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        today = fields.Date.today()
        refund = invoice.refund(
            date_invoice=today, date=today, description="A refund")
        self.assertEqual(picking.invoice_state, 'invoiced')
        self.assertIn(refund, picking.invoice_ids)
        self.assertIn(picking, refund.picking_ids)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEquals(nb_invoice_before,
                          nb_invoice_after - len(invoice | refund))

    def test_picking_invoicing_by_product1(self):
        """
        Test the invoice generation grouped by partner/product with 1
        picking and 2 moves.
        :return:
        """
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({'type': 'invoice'})
        picking = self.picking_model.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.pick_type_in.id,
            'location_id': self.location.id,
            'location_dest_id': self.location_dest.id,
        })
        move_vals = {
            'product_id': self.product.id,
            'picking_id': picking.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product.name,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        move_vals2 = {
            'product_id': self.product2.id,
            'picking_id': picking.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product2.name,
            'product_uom_qty': 1,
            'product_uom': self.product2.uom_id.id,
        }
        new_move2 = self.move_model.create(move_vals2)
        new_move.onchange_product_id()
        new_move2.onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, 'done')
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        # One invoice per partner but group products
        wizard_values.update({
            'group': 'partner_product',
        })
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        action = wizard.action_generate()
        domain = action.get('domain', [])
        invoice = self.invoice_model.search(domain)
        self.assertEqual(picking.invoice_state, 'invoiced')
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        products = invoice.invoice_line_ids.mapped("product_id")
        self.assertEquals(len(invoice.invoice_line_ids), 2)
        self.assertIn(self.product, products)
        self.assertIn(self.product2, products)
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEquals(nb_invoice_before, nb_invoice_after - len(invoice))

    def test_picking_invoicing_by_product2(self):
        """
        Test the invoice generation grouped by partner/product with 2
        picking and 2 moves per picking.
        We use same partner for 2 picking so we should have 1 invoice with 2
        lines (and qty 2)
        :return:
        """
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({'type': 'invoice'})
        picking = self.picking_model.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.pick_type_in.id,
            'location_id': self.location.id,
            'location_dest_id': self.location_dest.id,
        })
        move_vals = {
            'product_id': self.product.id,
            'picking_id': picking.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product.name,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        picking2 = picking.copy()
        move_vals2 = {
            'product_id': self.product.id,
            'picking_id': picking2.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product.name,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
        }
        new_move2 = self.move_model.create(move_vals2)
        new_move.onchange_product_id()
        new_move2.onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        picking2.set_to_be_invoiced()
        picking2.action_confirm()
        # Check product availability
        picking2.action_assign()
        # Force product availability
        for move in picking2.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking2.button_validate()
        self.assertEqual(picking.state, 'done')
        self.assertEqual(picking2.state, 'done')
        pickings = picking | picking2
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=pickings.ids,
            active_model=pickings._name,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        # One invoice per partner but group products
        wizard_values.update({
            'group': 'partner_product',
        })
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        action = wizard.action_generate()
        domain = action.get('domain', [])
        invoice = self.invoice_model.search(domain)
        self.assertEquals(len(invoice), 1)
        self.assertEqual(picking.invoice_state, 'invoiced')
        self.assertEqual(picking2.invoice_state, 'invoiced')
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(invoice, picking2.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        self.assertIn(picking2, invoice.picking_ids)
        products = invoice.invoice_line_ids.mapped("product_id")
        self.assertIn(self.product, products)
        for line in invoice.invoice_line_ids:
            # qty = 3 because 1 move + duplicate one + 1 new
            self.assertAlmostEqual(line.quantity, 3)
        # Now test behaviour if the invoice is delete
        invoice.unlink()
        for picking in pickings:
            self.assertEquals(picking.invoice_state, "2binvoiced")
        nb_invoice_after = self.invoice_model.search_count([])
        # Should be equals because we delete the invoice
        self.assertEquals(nb_invoice_before, nb_invoice_after)

        # Check method counting 2binvoice used in kanban view
        self.assertEquals(2, self.pick_type_in.count_picking_2binvoiced)

    def test_picking_invoicing_by_product3(self):
        """
        Test the invoice generation grouped by partner/product with 2
        picking and 2 moves per picking.
        We use different partner for 2 picking so we should have 2 invoice
        with 2 lines (and qty 1)
        :return:
        """
        nb_invoice_before = self.invoice_model.search_count([])
        self.partner.write({'type': 'invoice'})
        picking = self.picking_model.create({
            'partner_id': self.partner.id,
            'picking_type_id': self.pick_type_in.id,
            'location_id': self.location.id,
            'location_dest_id': self.location_dest.id,
        })
        move_vals = {
            'product_id': self.product.id,
            'picking_id': picking.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product.name,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        picking2 = picking.copy({
            'partner_id': self.partner3.id,
        })
        move_vals2 = {
            'product_id': self.product2.id,
            'picking_id': picking2.id,
            'location_dest_id': self.location_dest.id,
            'location_id': self.location.id,
            'name': self.product2.name,
            'product_uom_qty': 1,
            'product_uom': self.product2.uom_id.id,
        }
        new_move2 = self.move_model.create(move_vals2)
        new_move.onchange_product_id()
        new_move2.onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        picking2.set_to_be_invoiced()
        picking2.action_confirm()
        # Check product availability
        picking2.action_assign()
        # Force product availability
        for move in picking2.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking2.button_validate()
        self.assertEqual(picking.state, 'done')
        self.assertEqual(picking2.state, 'done')
        pickings = picking | picking2
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=pickings.ids,
            active_model=pickings._name,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        # One invoice per partner but group products
        wizard_values.update({
            'group': 'partner_product',
        })
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        action = wizard.action_generate()
        domain = action.get('domain', [])
        invoices = self.invoice_model.search(domain)
        self.assertEquals(len(invoices), 2)
        self.assertEqual(picking.invoice_state, 'invoiced')
        self.assertEqual(picking2.invoice_state, 'invoiced')
        self.assertIn(self.partner, invoices.mapped("partner_id"))
        self.assertIn(self.partner3, invoices.mapped("partner_id"))
        for invoice in invoices:
            self.assertEquals(len(invoice.picking_ids), 1)
            picking = invoice.picking_ids
            self.assertIn(invoice, picking.invoice_ids)
            for line in invoice.invoice_line_ids:
                self.assertAlmostEqual(line.quantity, 1)
            # Test the behaviour when the invoice is cancelled
            # The picking invoice_status should be updated
            invoice.action_cancel()
            self.assertEquals(picking.invoice_state, "2binvoiced")
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEquals(nb_invoice_before, nb_invoice_after - len(invoices))
