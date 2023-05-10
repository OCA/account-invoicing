# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions
from odoo.tests import Form, TransactionCase


class TestPickingInvoicing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_model = cls.env["stock.picking"]
        cls.move_model = cls.env["stock.move"]
        cls.invoice_wizard = cls.env["stock.invoice.onshipping"]
        cls.invoice_model = cls.env["account.move"]
        cls.partner_model = cls.env["res.partner"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner2 = cls.env.ref("base.res_partner_address_4")
        cls.partner3 = cls.env.ref("base.res_partner_18")
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.pick_type_in = cls.env.ref("stock.picking_type_in")
        cls.pick_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.suppliers_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_return_picking = cls.env["stock.return.picking"]
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "A super journal name",
                "code": "ABC",
                "type": "sale",
                "refund_sequence": True,
            }
        )

        cls.product_model = cls.env["product.product"]
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        cls.fiscal_position_tax_model = cls.env["account.fiscal.position.tax"]
        cls.fiscal_position_account_model = cls.env["account.fiscal.position.account"]
        cls.account_user_type = cls.env.ref("account.data_account_type_revenue")
        cls.account_model = cls.env["account.account"]
        cls.tax_model = cls.env["account.tax"]
        cls.product_tmpl_model = cls.env["product.template"]
        cls.account_receivable = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        cls.account_revenue = cls.env["account.account"].search(
            [("user_type_id", "=", cls.account_user_type.id)], limit=1
        )

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

        cls.product_test_1 = cls.product_model.create(
            {
                "name": "Test 1",
                "lst_price": "15000",
                "taxes_id": [(6, 0, [cls.tax_sale_1.id, cls.tax_sale_2.id])],
                "supplier_taxes_id": [
                    (6, 0, [cls.tax_purchase_1.id, cls.tax_purchase_2.id])
                ],
                "property_account_income_id": cls.account_revenue.id,
                "standard_price": "500",
            }
        )
        cls.product_test_2 = cls.product_model.create(
            {
                "name": "Test 2",
                "lst_price": "15000",
                "taxes_id": [(6, 0, [cls.tax_sale_1.id, cls.tax_sale_2.id])],
                "supplier_taxes_id": [
                    (6, 0, [cls.tax_purchase_1.id, cls.tax_purchase_2.id])
                ],
                "property_account_income_id": cls.account_revenue.id,
                "standard_price": "500",
            }
        )

    def test_0_picking_out_invoicing(self):
        # setting Agrolait type to default, because it's 'contact' in demo data
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
            "name": self.product_test_1.name,
            "product_uom_qty": 2,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move._onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)
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
            for mv_line in inv_line.move_line_ids:
                self.assertEqual(
                    mv_line.id,
                    new_move.id,
                    "Error to link stock.move with invoice.line.",
                )

    def test_1_picking_out_invoicing(self):
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
            "name": self.product_test_1.name,
            "product_uom_qty": 2,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move._onchange_product_id()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")
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
            wizard.with_context(lang="en_US").action_generate()
        msg = "No invoice created!"
        self.assertIn(msg, e.exception.args[0])
        nb_invoice_after = self.invoice_model.search_count([])
        self.assertEqual(nb_invoice_before, nb_invoice_after)

    def test_2_picking_out_invoicing(self):
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
            "name": self.product_test_1.name,
            "product_uom_qty": 2,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move._onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard_values.update({"group": "partner"})
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)
        # invoice = picking.invoice_ids[0]
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

    def test_3_picking_out_invoicing(self):
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
            "name": self.product_test_1.name,
            "product_uom_qty": 2,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move._onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)
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

    def test_4_picking_out_invoicing_backorder(self):
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
            "name": self.product_test_1.name,
            "product_uom_qty": 4,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move._onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty / 2.0

        backorder_action = picking.button_validate()
        Form(
            self.env[(backorder_action.get("res_model"))].with_context(
                **backorder_action["context"]
            )
        ).save().process()
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        backorder.action_assign()
        self.assertEqual(backorder.invoice_state, "2binvoiced")

        self.assertEqual(picking.state, "done")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)
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

    def test_picking_cancel(self):
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
            "name": self.product_test_1.name,
            "product_uom_qty": 2,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move._onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard_values.update({"group": "partner"})
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)
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

    def test_picking_invoice_refund(self):
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
            "name": self.product_test_1.name,
            "product_uom_qty": 2,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        new_move._onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard_values.update({"group": "partner"})
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)
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

    def test_picking_invoicing_by_product1(self):
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
            "name": self.product_test_1.name,
            "product_uom_qty": 1,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        move_vals2 = {
            "product_id": self.product_test_2.id,
            "picking_id": picking.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "name": self.product_test_2.name,
            "product_uom_qty": 1,
            "product_uom": self.product_test_2.uom_id.id,
        }
        new_move2 = self.move_model.create(move_vals2)
        new_move._onchange_product_id()
        new_move2._onchange_product_id()
        picking.set_to_be_invoiced()
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        # One invoice per partner but group products
        wizard_values.update({"group": "partner_product"})
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)
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

    def test_picking_invoicing_by_product2(self):
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
            "name": self.product_test_1.name,
            "product_uom_qty": 1,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        picking2 = picking.copy()
        move_vals2 = {
            "product_id": self.product_test_1.id,
            "picking_id": picking2.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "name": self.product_test_1.name,
            "product_uom_qty": 1,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move2 = self.move_model.create(move_vals2)
        new_move._onchange_product_id()
        new_move2._onchange_product_id()
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
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking2.state, "done")
        pickings = picking | picking2
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=pickings.ids,
            active_model=pickings._name,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        # One invoice per partner but group products
        wizard_values.update({"group": "partner_product"})
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)
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

    def test_picking_invoicing_by_product3(self):
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
            "name": self.product_test_1.name,
            "product_uom_qty": 1,
            "product_uom": self.product_test_1.uom_id.id,
        }
        new_move = self.move_model.create(move_vals)
        picking2 = picking.copy({"partner_id": self.partner3.id})
        move_vals2 = {
            "product_id": self.product_test_2.id,
            "picking_id": picking2.id,
            "location_dest_id": self.customers_location.id,
            "location_id": self.stock_location.id,
            "name": self.product_test_2.name,
            "product_uom_qty": 1,
            "product_uom": self.product_test_2.uom_id.id,
        }
        new_move2 = self.move_model.create(move_vals2)
        new_move._onchange_product_id()
        new_move2._onchange_product_id()
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
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking2.state, "done")
        pickings = picking | picking2
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=pickings.ids,
            active_model=pickings._name,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        # One invoice per partner but group products
        wizard_values.update({"group": "partner_product"})
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "in", [picking.id, picking2.id])]
        invoices = self.invoice_model.search(domain)
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

    def test_0_counting_2binvoiced(self):
        """
        Check method counting 2binvoice used in kanban view
        """
        self.assertEqual(1, self.pick_type_in.count_picking_2binvoiced)

    def test_return_customer_picking(self):
        """
        Test Return Customer Picking and Invoice created.
        """
        picking = self.env.ref("stock_picking_invoicing.stock_picking_invoicing_2")
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids,
            active_model=picking._name,
            active_id=picking.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)
        # Confirm Invoice
        invoice.action_post()
        self.assertEqual(invoice.state, "posted", "Invoice should be in state Posted")
        # Check Invoice Type
        self.assertEqual(
            invoice.move_type, "out_invoice", "Invoice Type should be Out Invoice"
        )

        # Return Picking
        return_wizard_form = Form(
            self.stock_return_picking.with_context(
                **dict(active_id=picking.id, active_model="stock.picking")
            )
        )
        return_wizard_form.invoice_state = "2binvoiced"
        self.return_wizard = return_wizard_form.save()

        result_wizard = self.return_wizard.create_returns()
        self.assertTrue(result_wizard, "Create returns wizard fail.")
        picking_devolution = self.env["stock.picking"].browse(
            result_wizard.get("res_id")
        )

        self.assertEqual(picking_devolution.invoice_state, "2binvoiced")
        for line in picking_devolution.move_lines:
            self.assertEqual(line.invoice_state, "2binvoiced")

        picking_devolution.action_confirm()
        picking_devolution.action_assign()
        # Force product availability
        for move in picking_devolution.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking_devolution.button_validate()
        self.assertEqual(picking_devolution.state, "done", "Change state fail.")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking_devolution.ids,
            active_model=picking_devolution._name,
            active_id=picking_devolution.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking_devolution.id)]
        invoice_devolution = self.invoice_model.search(domain)
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

    def test_return_supplier_picking(self):
        """
        Test Return Supplier Picking and Invoice created.
        """
        picking = self.env.ref("stock_picking_invoicing.stock_picking_invoicing_7")
        # Force product availability
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking.ids, active_model=picking._name, active_id=picking.id
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking.id)]
        invoice = self.invoice_model.search(domain)
        # Confirm Invoice
        invoice.action_post()
        self.assertEqual(invoice.state, "posted", "Invoice should be in state Posted")
        # Check Invoice Type
        self.assertEqual(
            invoice.move_type, "in_invoice", "Invoice Type should be In Invoice"
        )

        # Return Picking
        return_wizard_form = Form(
            self.stock_return_picking.with_context(
                **dict(active_id=picking.id, active_model="stock.picking")
            )
        )
        return_wizard_form.invoice_state = "2binvoiced"
        self.return_wizard = return_wizard_form.save()

        result_wizard = self.return_wizard.create_returns()
        self.assertTrue(result_wizard, "Create returns wizard fail.")
        picking_devolution = self.env["stock.picking"].browse(
            result_wizard.get("res_id")
        )

        self.assertEqual(picking_devolution.invoice_state, "2binvoiced")
        for line in picking_devolution.move_lines:
            self.assertEqual(line.invoice_state, "2binvoiced")

        picking_devolution.action_confirm()
        picking_devolution.action_assign()
        # Force product availability
        for move in picking_devolution.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking_devolution.button_validate()
        self.assertEqual(picking_devolution.state, "done", "Change state fail.")
        wizard_obj = self.invoice_wizard.with_context(
            active_ids=picking_devolution.ids,
            active_model=picking_devolution._name,
            active_id=picking_devolution.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        wizard = wizard_obj.create(wizard_values)
        wizard.onchange_group()
        wizard.action_generate()
        domain = [("picking_ids", "=", picking_devolution.id)]
        invoice_devolution = self.invoice_model.search(domain)
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
