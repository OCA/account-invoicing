from odoo.tests import tagged
from odoo.tests.common import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestGeneralLedgerReport(AccountTestInvoicingCommon):
    """
    Test that when creating an invoice from a picking,
    the invoice is correctly generated with the expected lines:
    All test are done with the following data:
    Purchase Line 1: product_1, 10 units, price 100
    Purchase Line 2: product_2, 20 units, price 200
    """

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "standard_price": 100,
                "list_price": 150,
                "type": "product",
                "purchase_method": "receive",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "product_2",
                "standard_price": 200,
                "list_price": 300,
                "type": "product",
                "purchase_method": "receive",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {"partner_id": cls.partner.id}
        )
        cls.purchase_line_1 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product_1.id,
                "product_qty": 10,
                "product_uom": cls.product_1.uom_id.id,
                "price_unit": 100,
            }
        )
        cls.purchase_line_2 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product_2.id,
                "product_qty": 20,
                "product_uom": cls.product_2.uom_id.id,
                "price_unit": 200,
            }
        )

    def test_search_picking(self):
        """
        Test that the search method returns the correct picking
        """
        Picking = self.env["stock.picking"].with_context(
            filter_picking_autocomplete=True,
            invoice_company_id=self.purchase_order.company_id.id,
            invoice_partner_id=self.purchase_order.partner_id.id,
        )
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        picking.move_line_ids.filtered(lambda x: x.product_id == self.product_1).write(
            {"qty_done": 10}
        )
        picking.move_line_ids.filtered(lambda x: x.product_id == self.product_2).write(
            {"qty_done": 20}
        )
        picking._action_done()
        picking_find = Picking.name_search(picking.name)
        self.assertEqual(len(picking_find), 1)
        self.assertEqual(picking_find[0][0], picking.id)
        # invoice the picking and check that it is not returned by the search
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        move_form.autocomplete_purchase_picking_id = picking
        move_form.save()
        picking_find = Picking.name_search(picking.name)
        self.assertEqual(len(picking_find), 0)

    def test_search_picking_by_po(self):
        """
        Test that the search method returns the correct picking
        - search by partner ref
        - search by purchase name
        """
        Picking = self.env["stock.picking"].with_context(
            filter_picking_autocomplete=True,
            invoice_company_id=self.purchase_order.company_id.id,
            invoice_partner_id=self.purchase_order.partner_id.id,
        )
        self.purchase_order.partner_ref = "Partner ref"
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        picking.move_line_ids.filtered(lambda x: x.product_id == self.product_1).write(
            {"qty_done": 10}
        )
        picking.move_line_ids.filtered(lambda x: x.product_id == self.product_2).write(
            {"qty_done": 20}
        )
        picking._action_done()
        # search by partner ref
        picking_find = Picking.name_search("Partner ref")
        self.assertEqual(len(picking_find), 1)
        self.assertEqual(picking_find[0][0], picking.id)
        # search by purchase name
        picking_find = Picking.name_search(self.purchase_order.name)
        self.assertEqual(len(picking_find), 1)
        self.assertEqual(picking_find[0][0], picking.id)
        # invoice the picking and check that it is not returned by the search
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        move_form.autocomplete_purchase_picking_id = picking
        move_form.save()
        picking_find = Picking.name_search("Partner ref")
        self.assertEqual(len(picking_find), 0)
        picking_find = Picking.name_search(self.purchase_order.name)
        self.assertEqual(len(picking_find), 0)

    def test_invoice_one_picking_one_invoice(self):
        """
        Receive 10 units of product_1 and 20 units of product_2.
        Check that the invoice has 2 lines with the correct quantities and prices.
        """
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        move_line_1 = picking.move_line_ids.filtered(
            lambda x: x.product_id == self.product_1
        )
        move_line_2 = picking.move_line_ids.filtered(
            lambda x: x.product_id == self.product_2
        )
        move_line_1.write({"qty_done": 10})
        move_line_2.write({"qty_done": 20})
        picking._action_done()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.received_invoiced_status, "to invoice")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 10)
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 20)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 20)
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        # fill the field and check that the invoice is correctly generated
        move_form.autocomplete_purchase_picking_id = picking
        new_invoice = move_form.save()
        self.assertEqual(new_invoice.invoice_origin, self.purchase_order.name)
        self.assertEqual(len(new_invoice.invoice_line_ids), 2)
        invoice_line1 = new_invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_1
        )
        invoice_line2 = new_invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_2
        )
        self.assertEqual(invoice_line1.quantity, 10)
        self.assertEqual(invoice_line1.price_unit, 100)
        self.assertEqual(invoice_line2.quantity, 20)
        self.assertEqual(invoice_line2.price_unit, 200)
        self.assertEqual(invoice_line1.stock_move_invoiced_id, move_line_1.move_id)
        self.assertEqual(invoice_line2.stock_move_invoiced_id, move_line_2.move_id)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_1.qty_invoiced, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_2.qty_invoiced, 20)
        self.assertEqual(picking.received_invoiced_status, "invoiced")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_1.move_id.qty_received_invoiced, 10)
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_2.move_id.qty_received_invoiced, 20)

    def test_invoice_two_picking_two_invoice(self):
        """
        Receive 10 units of product_1
        Check that the invoice 1 has 1 lines with the correct quantities and prices.
        Receive 20 units of product_2.
        Check that the invoice 2 has 1 lines with the correct quantities and prices.
        """
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        move_line_1 = picking.move_line_ids.filtered(
            lambda x: x.product_id == self.product_1
        )
        move_line_1.write({"qty_done": 10})
        picking._action_done()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.received_invoiced_status, "to invoice")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 10)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 0)  # no received yet
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        # fill the field and check that the invoice is correctly generated
        move_form.autocomplete_purchase_picking_id = picking
        new_invoice = move_form.save()
        self.assertEqual(new_invoice.invoice_origin, self.purchase_order.name)
        self.assertEqual(len(new_invoice.invoice_line_ids), 1)
        self.assertEqual(new_invoice.invoice_line_ids.product_id, self.product_1)
        self.assertEqual(new_invoice.invoice_line_ids.quantity, 10)
        self.assertEqual(new_invoice.invoice_line_ids.price_unit, 100)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 0)  # invoiced already
        self.assertEqual(self.purchase_line_1.qty_invoiced, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 0)  # no received yet
        self.assertEqual(self.purchase_line_2.qty_invoiced, 0)
        self.assertEqual(len(self.purchase_order.invoice_ids), 1)
        self.assertEqual(picking.received_invoiced_status, "invoiced")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_1.move_id.qty_received_invoiced, 10)
        # process the second picking with a new invoice
        picking2 = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        move_line_2 = picking2.move_line_ids.filtered(
            lambda x: x.product_id == self.product_2
        )
        move_line_2.write({"qty_done": 20})
        picking2._action_done()
        self.assertEqual(picking2.state, "done")
        self.assertEqual(picking2.received_invoiced_status, "to invoice")
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 20)
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 20)
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        # fill the field and check that the invoice is correctly generated
        move_form.autocomplete_purchase_picking_id = picking2
        new_invoice = move_form.save()
        self.assertEqual(new_invoice.invoice_origin, self.purchase_order.name)
        self.assertEqual(len(new_invoice.invoice_line_ids), 1)
        self.assertEqual(new_invoice.invoice_line_ids.product_id, self.product_2)
        self.assertEqual(new_invoice.invoice_line_ids.quantity, 20)
        self.assertEqual(new_invoice.invoice_line_ids.price_unit, 200)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_1.qty_invoiced, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_2.qty_invoiced, 20)
        self.assertEqual(len(self.purchase_order.invoice_ids), 2)
        self.assertEqual(picking2.received_invoiced_status, "invoiced")
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_2.move_id.qty_received_invoiced, 20)

    def test_invoice_two_picking_one_invoice(self):
        """
        Receive 10 units of product_1
        Receive 20 units of product_2.
        Check that the invoice 1 has 2 lines with the correct quantities and prices.
        """
        self.purchase_order.button_confirm()
        # process the first picking
        picking = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        move_line_1 = picking.move_line_ids.filtered(
            lambda x: x.product_id == self.product_1
        )
        move_line_1.write({"qty_done": 10})
        picking._action_done()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.received_invoiced_status, "to invoice")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 10)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 0)  # no received yet
        # process the second picking
        picking2 = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        move_line_2 = picking2.move_line_ids.filtered(
            lambda x: x.product_id == self.product_2
        )
        move_line_2.write({"qty_done": 20})
        picking2._action_done()
        self.assertEqual(picking2.state, "done")
        self.assertEqual(picking2.received_invoiced_status, "to invoice")
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 20)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 20)
        # create the invoice
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        # fill the first picking
        move_form.autocomplete_purchase_picking_id = picking
        invoice = move_form.save()
        self.assertEqual(invoice.invoice_origin, self.purchase_order.name)
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertEqual(invoice.invoice_line_ids.product_id, self.product_1)
        self.assertEqual(invoice.invoice_line_ids.quantity, 10)
        self.assertEqual(invoice.invoice_line_ids.price_unit, 100)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 0)  # invoiced already
        self.assertEqual(self.purchase_line_1.qty_invoiced, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 20)  # no invoiced yet
        self.assertEqual(self.purchase_line_2.qty_invoiced, 0)
        self.assertEqual(len(self.purchase_order.invoice_ids), 1)
        self.assertEqual(picking.received_invoiced_status, "invoiced")
        self.assertEqual(picking2.received_invoiced_status, "to invoice")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_1.move_id.qty_received_invoiced, 10)
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 20)
        self.assertEqual(move_line_2.move_id.qty_received_invoiced, 0)
        # fill the second picking in the same invoice
        move_form = Form(invoice)
        move_form.autocomplete_purchase_picking_id = picking2
        invoice = move_form.save()
        self.assertEqual(len(invoice.invoice_line_ids), 2)
        invoice_line1 = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_1
        )
        invoice_line2 = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_2
        )
        self.assertEqual(invoice_line1.product_id, self.product_1)
        self.assertEqual(invoice_line1.quantity, 10)
        self.assertEqual(invoice_line1.price_unit, 100)
        self.assertEqual(invoice_line1.stock_move_invoiced_id, move_line_1.move_id)
        self.assertEqual(invoice_line2.product_id, self.product_2)
        self.assertEqual(invoice_line2.quantity, 20)
        self.assertEqual(invoice_line2.price_unit, 200)
        self.assertEqual(invoice_line2.stock_move_invoiced_id, move_line_2.move_id)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_1.qty_invoiced, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_2.qty_invoiced, 20)
        self.assertEqual(len(self.purchase_order.invoice_ids), 1)
        self.assertEqual(picking.received_invoiced_status, "invoiced")
        self.assertEqual(picking2.received_invoiced_status, "invoiced")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_1.move_id.qty_received_invoiced, 10)
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_2.move_id.qty_received_invoiced, 20)

    def test_invoice_two_picking_one_invoice_partial(self):
        """
        Picking 1:
            Receive 6 units of product_1
            Receive 15 units of product_2.
        Picking 2:
            Receive 4 units of product_1
            Receive 5 units of product_2.
        """
        self.purchase_order.button_confirm()
        # process the first picking
        picking = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        move_line_1 = picking.move_line_ids.filtered(
            lambda x: x.product_id == self.product_1
        )
        move_line_2 = picking.move_line_ids.filtered(
            lambda x: x.product_id == self.product_2
        )
        move_line_1.write({"qty_done": 6})
        move_line_2.write({"qty_done": 15})
        picking._action_done()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.received_invoiced_status, "to invoice")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 6)
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 15)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 6)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 15)
        # process the second picking
        picking2 = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        move_line_3 = picking2.move_line_ids.filtered(
            lambda x: x.product_id == self.product_1
        )
        move_line_4 = picking2.move_line_ids.filtered(
            lambda x: x.product_id == self.product_2
        )
        move_line_3.write({"qty_done": 4})
        move_line_4.write({"qty_done": 5})
        picking2._action_done()
        self.assertEqual(picking2.state, "done")
        self.assertEqual(picking2.received_invoiced_status, "to invoice")
        self.assertEqual(move_line_3.move_id.qty_received_to_invoice, 4)
        self.assertEqual(move_line_4.move_id.qty_received_to_invoice, 5)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 20)
        # create the invoice
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        # fill the first picking
        move_form.autocomplete_purchase_picking_id = picking
        invoice = move_form.save()
        self.assertEqual(invoice.invoice_origin, self.purchase_order.name)
        self.assertEqual(len(invoice.invoice_line_ids), 2)
        invoice_line_1 = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_1
            and x.picking_invoiced_id == picking
        )
        invoice_line_2 = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_2
            and x.picking_invoiced_id == picking
        )
        self.assertEqual(invoice_line_1.quantity, 6)
        self.assertEqual(invoice_line_1.price_unit, 100)
        self.assertEqual(invoice_line_1.stock_move_invoiced_id, move_line_1.move_id)
        self.assertEqual(invoice_line_2.quantity, 15)
        self.assertEqual(invoice_line_2.price_unit, 200)
        self.assertEqual(invoice_line_2.stock_move_invoiced_id, move_line_2.move_id)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 4)
        self.assertEqual(self.purchase_line_1.qty_invoiced, 6)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 5)
        self.assertEqual(self.purchase_line_2.qty_invoiced, 15)
        self.assertEqual(len(self.purchase_order.invoice_ids), 1)
        self.assertEqual(picking.received_invoiced_status, "invoiced")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_1.move_id.qty_received_invoiced, 6)
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_2.move_id.qty_received_invoiced, 15)
        # fill the second picking in the same invoice
        move_form = Form(invoice)
        move_form.autocomplete_purchase_picking_id = picking2
        invoice = move_form.save()
        self.assertEqual(invoice.invoice_origin, self.purchase_order.name)
        self.assertEqual(len(invoice.invoice_line_ids), 4)
        invoice_line_3 = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_1
            and x.picking_invoiced_id == picking2
        )
        invoice_line_4 = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_2
            and x.picking_invoiced_id == picking2
        )
        self.assertEqual(invoice_line_3.quantity, 4)
        self.assertEqual(invoice_line_3.price_unit, 100)
        self.assertEqual(invoice_line_3.stock_move_invoiced_id, move_line_3.move_id)
        self.assertEqual(invoice_line_4.quantity, 5)
        self.assertEqual(invoice_line_4.price_unit, 200)
        self.assertEqual(invoice_line_4.stock_move_invoiced_id, move_line_4.move_id)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_1.qty_invoiced, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_2.qty_invoiced, 20)
        self.assertEqual(len(self.purchase_order.invoice_ids), 1)
        self.assertEqual(picking2.received_invoiced_status, "invoiced")
        self.assertEqual(move_line_3.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_3.move_id.qty_received_invoiced, 4)
        self.assertEqual(move_line_4.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_4.move_id.qty_received_invoiced, 5)

    def test_other_uom(self):
        """
        Picking 1:
            Receive 10 units of product_1
            Receive 2 Dozen of product_2.
        """
        self.purchase_line_2.write(
            {
                "product_uom": self.env.ref("uom.product_uom_dozen").id,
                "product_qty": 2,
            }
        )
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        move_line_1 = picking.move_line_ids.filtered(
            lambda x: x.product_id == self.product_1
        )
        move_line_2 = picking.move_line_ids.filtered(
            lambda x: x.product_id == self.product_2
        )
        move_line_1.write({"qty_done": 10})
        move_line_2.write({"qty_done": 24})
        picking._action_done()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.received_invoiced_status, "to invoice")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 10)
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 24)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 2)  # 2 dozen = 24 units
        # create the invoice
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        # fill the first picking
        move_form.autocomplete_purchase_picking_id = picking
        invoice = move_form.save()
        self.assertEqual(invoice.invoice_origin, self.purchase_order.name)
        self.assertEqual(len(invoice.invoice_line_ids), 2)
        invoice_line_1 = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_1
            and x.picking_invoiced_id == picking
        )
        invoice_line_2 = invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == self.product_2
            and x.picking_invoiced_id == picking
        )
        self.assertEqual(invoice_line_1.quantity, 10)
        self.assertEqual(invoice_line_1.price_unit, 100)
        self.assertEqual(invoice_line_1.stock_move_invoiced_id, move_line_1.move_id)
        self.assertEqual(invoice_line_2.quantity, 2)  # 2 dozen = 24 units
        self.assertEqual(invoice_line_2.price_unit, 200)
        self.assertEqual(invoice_line_2.stock_move_invoiced_id, move_line_2.move_id)
        self.assertEqual(self.purchase_line_1.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_1.qty_invoiced, 10)
        self.assertEqual(self.purchase_line_2.qty_to_invoice, 0)
        self.assertEqual(self.purchase_line_2.qty_invoiced, 2)
        self.assertEqual(len(self.purchase_order.invoice_ids), 1)
        self.assertEqual(picking.received_invoiced_status, "invoiced")
        self.assertEqual(move_line_1.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_1.move_id.qty_received_invoiced, 10)
        self.assertEqual(move_line_2.move_id.qty_received_to_invoice, 0)
        self.assertEqual(move_line_2.move_id.qty_received_invoiced, 24)
