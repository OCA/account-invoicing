# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions, models
from odoo.tests import Form

from odoo.addons.stock_picking_invoicing.tests.tools import (
    create_with_form_inv_onshipping,
    create_with_form_pck_backorder,
    create_with_form_return_picking,
)

from .common import TestSaleStockPickingInvoicingCommon
from .tools import (
    create_with_form_account_payment,
    create_with_form_sale_adv_pay_inv,
    get_tested_module_names,
)


class TestSaleStockPickingInvoicing(TestSaleStockPickingInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_sale_stock_return(self):
        """
        Test the values transferred from the Sale Order Line to the Stock
        Move of the Picking created by a confirmed Sale Order (only the
        fields provided by the modules under test and their dependencies
        are compared) and that a Sale Order of products only can not be
        invoiced from the Sale Order itself with the 'stock_picking'
        Invoicing Policy.
        """
        sale_order = self.sale_order_0

        # confirm our standard so, check the picking
        sale_order.action_confirm()
        self.assertTrue(
            sale_order.picking_ids,
            'Sale Stock: no picking created for "invoice on '
            'delivery" storable products',
        )

        # set stock.picking to be invoiced
        self.assertTrue(
            len(sale_order.picking_ids) == 1,
            "More than one stock picking for sale.order",
        )

        # Check Sale Invoicing Policy Warning to force create Invoice from Picking
        with self.assertRaises(exceptions.UserError):
            sale_order.with_context(active_model="sale.order")._create_invoices(
                final=True
            )

        sale_order.picking_ids.set_to_be_invoiced()

        # validate stock.picking
        stock_picking = sale_order.picking_ids
        # compare sale.order.line with stock.move
        stock_move = stock_picking.move_ids
        sale_order_line = sale_order.order_line

        move_fields = self.env["stock.move"]._fields
        line_fields = self.env["sale.order.line"]._fields

        skipped_fields = [
            "id",
            # Technical fields: both records are created/written by different
            # operations, so the tracking information is not equal.
            "create_date",
            "create_uid",
            "write_date",
            "write_uid",
            # The 'quantity' has a different meaning in each model: on the
            # Stock Move it is the done quantity (sum of the move lines) and on
            # the Sale Order Line the quantity to invoice.
            "quantity",
            # 'S00029/FURN_7777: Stock>Customers' != 'S00029 - Office Chair'
            "display_name",
            "state",
            # Price Unit in move is different from sale line
            # TODO: Should be equal? After Confirmed stock picking
            #  the value will be change based Stock Valuation
            #  configuration.
            "price_unit",
            # There are a diference for field Name
            # '[FURN_7777] Office Chair' != 'Office Chair'
            "name",
        ]

        # Compare all the fields the two models have in common, but only the
        # ones provided by the modules under test and their dependencies:
        # fields added by other installed modules (localizations, ...) are set
        # by their own glue modules and tested by their own tests.
        tested_modules = get_tested_module_names(
            self.env, "sale_stock_picking_invoicing"
        )
        common_fields = [
            field
            for field in set(move_fields) & set(line_fields) - set(skipped_fields)
            if move_fields[field]._module in tested_modules
            and line_fields[field]._module in tested_modules
        ]

        for field in common_fields:
            self.assertEqual(
                stock_move[field],
                sale_order_line[field],
                f"Field {field} failed to transfer from sale.order.line to stock.move",
            )

    def test_02_picking_sale_order_product_and_service(self):
        """
        Test Sale Order with product and service
        """
        # Ensure the company's sale_invoicing_policy is set to "stock_picking"
        self.assertEqual(self.company.sale_invoicing_policy, "stock_picking")

        sale_order_2 = self.sale_order_2
        sale_order_2.action_confirm()
        # Method to create invoice in sale order should work only
        # for lines where products are of TYPE Service
        sale_order_2._create_invoices()
        # Should be exist one Invoice
        self.assertEqual(1, sale_order_2.invoice_count)
        for invoice in sale_order_2.invoice_ids:
            line = invoice.invoice_line_ids.filtered(
                lambda ln: ln.product_id.type == "service"
            )
            self.assertEqual(line.product_id.type, "service")
            # Invoice of Service
            invoice.action_post()
            self.assertEqual(
                invoice.state, "posted", "Invoice should be in state Posted"
            )

        picking = sale_order_2.picking_ids
        # Only the line of Type Product
        self.assertEqual(len(picking.move_ids_without_package), 1)
        self.assertEqual(picking.invoice_state, "2binvoiced")
        self.picking_move_state(picking)

        # Test Create Invoice from Sale when raise UseError
        context = {
            "active_model": "sale.order",
            "active_id": sale_order_2.id,
            "active_ids": sale_order_2.ids,
        }
        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(**context)
            .create(
                {
                    "advance_payment_method": "delivered",
                }
            )
        )
        with self.assertRaises(exceptions.UserError):
            payment.with_context(**context).create_invoices()

        invoice = create_with_form_inv_onshipping(self.env, picking)
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        # Picking with Partner Shipping from Sale Order
        self.assertEqual(picking.partner_id, sale_order_2.partner_shipping_id)
        # Invoice created with Partner Invoice from Sale Order
        self.assertEqual(invoice.partner_id, sale_order_2.partner_invoice_id)
        # Invoice created with Partner Shipping from Picking
        self.assertEqual(invoice.partner_shipping_id, picking.partner_id)
        # When informed Payment Term in Sale Orde should be
        # used instead of the default in Partner.
        self.assertEqual(invoice.invoice_payment_term_id, sale_order_2.payment_term_id)

        # 1 Product 1 Note should be created
        self.assertEqual(len(invoice.invoice_line_ids), 2)

        # In the Sale Order should be exist two Invoices, one
        # for Product other for Service
        self.assertEqual(2, sale_order_2.invoice_count)

        # Confirm Invoice
        invoice.action_post()
        self.assertEqual(invoice.state, "posted", "Invoice should be in state Posted.")

        # Check Invoiced QTY
        for line in sale_order_2.order_line.filtered(
            lambda ln: ln.product_id.is_storable
        ):
            self.assertEqual(line.product_uom_qty, line.qty_invoiced)
            # Test the qty_to_invoice
            line.product_id.invoice_policy = "order"
            self.assertEqual(line.qty_to_invoice, 0.0)

        # Check if the Sale Order Line fields are equals to Invoice Lines
        line_fields = self.env["sale.order.line"]._fields
        invoice_line_fields = self.env["account.move.line"]._fields

        skipped_fields = [
            "id",
            # Technical fields: both records are created/written by different
            # operations, so the tracking information is not equal.
            "create_date",
            "create_uid",
            "write_date",
            "write_uid",
            "__last_update",
            "display_name",
            "state",
            # By th TAX 15% automatic add in invoice the value change
            "price_total",
            # Field sequence add in creation of Invoice
            "sequence",
            # In the sale.orde.line display_type has only line_section
            # and line_note, the acccount.move.line has more options
            "display_type",
        ]

        # Compare all the fields the two models have in common, but only the
        # ones provided by the modules under test and their dependencies:
        # fields added by other installed modules (localizations, ...) are set
        # by their own glue modules and tested by their own tests.
        tested_modules = get_tested_module_names(
            self.env, "sale_stock_picking_invoicing"
        )
        common_fields = [
            field
            for field in set(invoice_line_fields)
            & set(line_fields) - set(skipped_fields)
            if invoice_line_fields[field]._module in tested_modules
            and line_fields[field]._module in tested_modules
        ]
        sale_order_line = picking.move_ids_without_package.filtered(
            lambda ln: ln.sale_line_id
        ).sale_line_id
        invoice_lines = picking.invoice_ids.invoice_line_ids.filtered(
            lambda ln: ln.product_id
        )
        # Necessary for get analytic_precision
        # this problem only occours in the tests, by some reason not
        # identify yet, but works in the screen the default behavior
        with Form(invoice_lines) as line:
            line.save()
        for field in common_fields:
            if (
                isinstance(sale_order_line[field], models.BaseModel)
                and sale_order_line[field]._name != invoice_lines[field]._name
            ):
                # Same name, different models
                # e.g.: sale_commmission_oca with agent_ids field
                continue
            self.assertEqual(
                sale_order_line[field],
                invoice_lines[field],
                f"Field {field} failed to transfer from sale.order.line "
                "to account.invoice.line",
            )

        # Return Picking
        picking_devolution = create_with_form_return_picking(self.env, picking)

        self.assertEqual(picking_devolution.invoice_state, "2binvoiced")
        for line in picking_devolution.move_ids:
            self.assertEqual(line.invoice_state, "2binvoiced")

        self.picking_move_state(picking_devolution)
        self.assertEqual(picking_devolution.state, "done", "Change state fail.")

        invoice_devolution = create_with_form_inv_onshipping(
            self.env, picking_devolution
        )
        # Confirm Invoice
        invoice_devolution.action_post()
        self.assertEqual(
            invoice_devolution.state, "posted", "Invoice should be in state Posted"
        )
        # Test need to be comment because there are a problem with module
        # sale_line_refund_to_invoice_qty
        # https://github.com/OCA/account-invoicing/blob/
        # 14.0/sale_line_refund_to_invoice_qty/models/sale.py#L20
        # when the tests run in CI of the repo the test fail.
        # TODO: The module should be compatible with this case?
        # Check Invoiced QTY update after Refund
        # for line in sale_order_2.order_line:
        #    # Check Product line
        #    if line.product_id.type == "product":
        #        # self.assertEqual(0.0, line.qty_invoiced)

    def test_03_picking_invoicing_partner_shipping_invoiced(self):
        """
        Test the invoice generation grouped by partner/product with 2
        picking and 2 moves per picking, but Partner to Shipping is
        different from Partner to Invoice.
        """
        picking = self.run_sale_picking_process(self.sale_order_1)
        sale_order_2 = self.sale_order_2
        sale_order_2.note = False
        picking2 = self.run_sale_picking_process(sale_order_2)
        pickings = picking | picking2
        invoice = create_with_form_inv_onshipping(self.env, pickings)
        # Groupping Invoice
        self.assertEqual(len(invoice), 1)
        # Invoice should be create with the partner_invoice_id
        self.assertEqual(invoice.partner_id, self.sale_order_1.partner_invoice_id)
        # Invoice partner shipping should be the same of picking
        self.assertEqual(invoice.partner_shipping_id, picking.partner_id)
        self.assertIn(invoice, picking.invoice_ids)
        self.assertIn(picking, invoice.picking_ids)
        self.assertIn(invoice, picking2.invoice_ids)
        self.assertIn(picking2, invoice.picking_ids)

        # TODO: Grouping sale line with KEY should be analise
        # self.assertEqual(len(invoice.invoice_line_ids), 2)
        # 3 Products, 2 Note and 2 Section
        self.assertEqual(len(invoice.invoice_line_ids), 7)
        for inv_line in invoice.invoice_line_ids.filtered(lambda ln: ln.product_id):
            self.assertTrue(inv_line.tax_ids, "Error to map Sale Tax in invoice.line.")
        # Post the Invoice to validate the fields
        invoice.action_post()

    def test_04_ungrouping_pickings_partner_shipping_different(self):
        """
        Test the invoice generation grouped by partner/product with 3
        picking and 2 moves per picking, the 3 has the same Partner to
        Invoice but one has Partner to Shipping so shouldn't be grouping.
        """
        picking = self.run_sale_picking_process(self.sale_order_1)
        picking3 = self.run_sale_picking_process(self.sale_order_3)
        picking4 = self.run_sale_picking_process(self.sale_order_4)

        pickings = picking | picking3 | picking4
        invoices = create_with_form_inv_onshipping(self.env, pickings)
        # Even with same Partner Invoice if the Partner Shipping
        # are different should not be Groupping
        self.assertEqual(len(invoices), 2)

        # Invoice that has different Partner Shipping
        # should be not groupping
        invoice_pick_1 = invoices.filtered(
            lambda t: t.partner_id != t.partner_shipping_id
        )
        # Invoice should be create with partner_invoice_id
        self.assertEqual(
            invoice_pick_1.partner_id, self.sale_order_1.partner_invoice_id
        )
        # Invoice create with Partner Shipping used in Picking
        self.assertEqual(invoice_pick_1.partner_shipping_id, picking.partner_id)

        # Groupping Invoice
        invoice_pick_3_4 = invoices.filtered(
            lambda t: t.partner_id == t.partner_shipping_id
        )
        self.assertIn(invoice_pick_3_4, picking3.invoice_ids)
        self.assertIn(invoice_pick_3_4, picking4.invoice_ids)
        # Check Re-sequence: the Invoice Lines must be in the same order of
        # the Sale Order Lines (Sale Order 3 first, then Sale Order 4)
        sale_order_lines = self.sale_order_3.order_line | self.sale_order_4.order_line
        inv_lines_by_sequence = {
            inv_line.sequence: inv_line
            for inv_line in invoice_pick_3_4.invoice_line_ids
        }
        for sequence, sale_line in enumerate(sale_order_lines):
            self.assertIn(
                sequence,
                inv_lines_by_sequence,
                "Error to Re-sequence Invoice Lines, sequence not found.",
            )
            self.assertEqual(
                sale_line.name,
                inv_lines_by_sequence[sequence].name,
                "Error to Re-sequence Invoice Lines from Sale Order Lines.",
            )

    def test_05_down_payment(self):
        """Test the case with Down Payment"""
        sale_order_1 = self.sale_order_1
        sale_order_1.action_confirm()

        invoice_down_payment = create_with_form_sale_adv_pay_inv(
            self.env,
            sale_order_1,
            {
                "advance_payment_method": "percentage",
                "amount": 50,
            },
        )
        invoice_down_payment.action_post()

        journal_cash = self.env["account.journal"].search(
            [
                ("type", "=", "cash"),
                ("company_id", "=", invoice_down_payment.company_id.id),
            ],
            limit=1,
        )
        payment = create_with_form_account_payment(
            self.env,
            invoice_down_payment,
            {"journal_id": journal_cash, "amount": invoice_down_payment.amount_total},
        )
        self.assertTrue(payment, "Payment not created by Down Payment test.")

        # A second Down Payment: the Invoice created from the Picking must
        # have only one dedicated Line Section for the Down Payments, with
        # one line for each of them, in the end of the Invoice
        # (`create_with_form_sale_adv_pay_inv` returns all the Sale Order
        # Invoices, so only the new draft one is posted)
        sale_order_invoices = create_with_form_sale_adv_pay_inv(
            self.env,
            sale_order_1,
            {"advance_payment_method": "percentage", "amount": 10},
        )
        sale_order_invoices.filtered(lambda inv: inv.state == "draft").action_post()

        picking = sale_order_1.picking_ids
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        # 2 Products, 1 Note, the Sale Order Section and 2 Down Payments
        # (the dedicated Line Section + 1 line for each Down Payment)
        self.assertEqual(len(invoice.invoice_line_ids), 7)
        line_section = invoice.invoice_line_ids.filtered(
            lambda line: line.display_type == "line_section"
        )
        self.assertEqual(
            len(line_section), 2, "Invoice without Line Section for Down Payment."
        )
        down_payment_lines = invoice.invoice_line_ids.filtered(
            lambda line: line.sale_line_ids.is_downpayment
        )
        self.assertEqual(
            len(down_payment_lines), 2, "Invoice without the Down Payment lines."
        )
        # The Down Payments lines are put in the end of the Invoice, after
        # the dedicated Line Section
        self.assertEqual(invoice.invoice_line_ids.ids[-2:], down_payment_lines.ids)
        self.assertEqual(invoice.invoice_line_ids[-3].display_type, "line_section")

    def test_06_default_value_sale_invoicing_policy(self):
        """Test default value for sale_invoicing_policy

        The default set by the module (res_company.
        _default_sale_invoicing_policy) depends on the database having demo
        data, so the expected value is read from it instead of being fixed.
        """
        company = self.env["res.company"].create(
            {
                "name": "Test",
            }
        )
        base_module = self.env["ir.module.module"].search([("name", "=", "base")])
        expected = "sale_order" if base_module.demo else "stock_picking"
        self.assertEqual(company.sale_invoicing_policy, expected)

    def test_07_picking_invocing_without_sale_order(self):
        """Test Picking Invoicing without Sale Order

        A Stock Move not related to a Sale Order Line must not inform the
        Picking as 'to be invoiced' (native behaviour, the user marks it
        with the 'To Be Invoiced' button) and the Invoice is created with
        the Picking data.
        """
        picking = self.picking_out_1
        move = picking.move_ids
        self.assertFalse(move.sale_line_id)
        self.assertEqual(
            move._get_new_picking_values().get("invoice_state", "none"), "none"
        )

        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        self.assertEqual(len(invoice), 1)

    def test_08_combo_product_invoicing(self):
        """
        Combo product with stock_picking policy: the combo header line and
        any service child must be invoiceable from the Sale Order; consu
        children must be invoiced from the related Stock Picking.
        """
        so = self.sale_order_5
        so.action_confirm()

        # Only consu children generate stock moves
        self.assertTrue(so.picking_ids, "Combo with consu items should create picking")
        picking = so.picking_ids
        picking_products = picking.move_ids.mapped("product_id")
        self.assertIn(self.product_storable_1, picking_products)
        self.assertIn(self.product_storable_2, picking_products)
        self.assertNotIn(self.product_service, picking_products)
        self.assertNotIn(self.product_combo, picking_products)

        # Invoicing from SO: combo header + service child, no consu
        so_invoice = so._create_invoices()
        self.assertEqual(len(so_invoice), 1)
        so_invoice_products = so_invoice.invoice_line_ids.mapped("product_id")
        self.assertIn(self.product_service, so_invoice_products)
        self.assertNotIn(self.product_storable_1, so_invoice_products)
        self.assertNotIn(self.product_storable_2, so_invoice_products)
        self.assertTrue(
            so_invoice.invoice_line_ids.filtered(
                lambda ln: ln.display_type == "line_section"
            ),
            "Combo header line should appear as a section on the SO invoice",
        )
        so_invoice.action_post()
        self.assertEqual(so_invoice.state, "posted")

        # Invoicing from picking: only consu children
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        picking_invoice = create_with_form_inv_onshipping(self.env, picking)
        self.assertEqual(len(picking_invoice), 1)
        picking_invoice_products = picking_invoice.invoice_line_ids.mapped("product_id")
        self.assertIn(self.product_storable_1, picking_invoice_products)
        self.assertIn(self.product_storable_2, picking_invoice_products)
        self.assertNotIn(self.product_service, picking_invoice_products)
        self.assertTrue(
            picking_invoice.invoice_line_ids.filtered(
                lambda ln: (
                    ln.display_type == "line_section"
                    and ln.name == self.product_combo.name
                )
            ),
            "Combo header should appear as a section on the picking invoice",
        )
        picking_invoice.action_post()
        self.assertEqual(picking_invoice.state, "posted")

    def test_09_combo_product_invoicing_picking_first(self):
        """
        Reverse flow: invoice the picking before the Sale Order. The combo
        header must still appear on the later SO invoice.
        """
        so = self.sale_order_5
        picking = self.run_sale_picking_process(so)

        # Invoice the picking first
        picking_invoice = create_with_form_inv_onshipping(self.env, picking)
        self.assertTrue(
            picking_invoice.invoice_line_ids.filtered(
                lambda ln: (
                    ln.display_type == "line_section"
                    and ln.name == self.product_combo.name
                )
            ),
            "Combo header should appear as a section on the picking invoice",
        )
        picking_invoice.action_post()

        # Then invoice the SO: combo header must still show up
        so_invoice = so._create_invoices()
        self.assertEqual(len(so_invoice), 1)
        self.assertIn(
            self.product_service, so_invoice.invoice_line_ids.mapped("product_id")
        )
        self.assertTrue(
            so_invoice.invoice_line_ids.filtered(
                lambda ln: ln.display_type == "line_section"
            ),
            "Combo header line should still appear on the SO invoice when "
            "the picking has already been invoiced",
        )
        so_invoice.action_post()
        self.assertEqual(so_invoice.state, "posted")

    def test_10_so_only_consu_with_notes_invoice_from_so_raises(self):
        """
        Under 'stock_picking', a SO whose only invoiceable content is
        consu products (plus note/section lines) must raise the explicit
        "invoice from the picking" error, instead of returning the
        note/section lines and failing with Odoo's generic
        "No items are available to invoice".
        """
        self.assertEqual(self.company.sale_invoicing_policy, "stock_picking")
        # sale_order_3 = 2 consu products + 1 note + 1 section, no service
        picking = self.run_sale_picking_process(self.sale_order_3)
        self.assertEqual(picking.state, "done")
        with self.assertRaises(exceptions.UserError) as e:
            self.sale_order_3.with_context(active_model="sale.order")._create_invoices(
                final=True
            )
        self.assertIn("Sale Invoicing Policy", e.exception.args[0])

    def test_11_both_policy_invoices_from_so_mark_pickings(self):
        """'both' policy: invoicing from the Sale Order marks the Pickings as
        invoiced.

        The behaviour does not depend on the delivery state:

        - Picking validated (delivered): it is marked as invoiced when the
          quantities are invoiced from the Sale Order;
        - Picking not validated yet: with the 'order' invoice policy the whole
          ordered quantity is invoiced from the Sale Order, so the Picking is
          marked as invoiced as well;
        - Full delivery and Invoice from the Sale Order: the Picking Wizard must
          not create a second Invoice (no duplicated Invoice);
        - Partial delivery with a `backorder`: the delivered Picking AND the
          `backorder` are marked as invoiced, nothing is left to invoice in the
          Sale Order Line.
        """
        # 1) Validated Picking (delivered)
        sale_order = self._create_confirmed_sale_order()
        picking = sale_order.picking_ids
        self.assertEqual(picking.invoice_state, "2binvoiced")

        # Validate picking
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")

        # Invoice from the sale order
        sale_order._create_invoices(final=True)
        self.assertEqual(sale_order.invoice_count, 1)

        # Picking and moves should be marked as invoiced
        self.assertEqual(picking.invoice_state, "invoiced")
        for move in picking.move_ids:
            self.assertEqual(move.invoice_state, "invoiced")

        # Post the invoice
        invoice = sale_order.invoice_ids
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

        # 2) Picking not validated yet
        # The same happens when the Picking is not validated yet: with the
        # 'order' invoice policy the whole ordered quantity is invoiced from
        # the Sale Order, so the Picking must be marked as invoiced as well
        sale_order_not_delivered = self._create_confirmed_sale_order(qty=3.0)
        picking_not_delivered = sale_order_not_delivered.picking_ids
        self.assertEqual(picking_not_delivered.invoice_state, "2binvoiced")
        self.assertNotEqual(picking_not_delivered.state, "done")

        sale_order_not_delivered._create_invoices(final=True)
        self.assertEqual(sale_order_not_delivered.invoice_count, 1)

        self.assertEqual(picking_not_delivered.invoice_state, "invoiced")
        for move in picking_not_delivered.move_ids:
            self.assertEqual(move.invoice_state, "invoiced")

        # 3) Full delivery and Invoice from the Sale Order: the Wizard does not
        # invoice the Picking again
        sale_order = self._create_confirmed_sale_order(qty=5.0)
        picking = sale_order.picking_ids
        self.picking_move_state(picking)
        self.assertEqual(picking.state, "done")

        # Full invoice from the SO
        sale_order._create_invoices(final=True)
        self.assertEqual(sale_order.invoice_count, 1)
        self.assertEqual(picking.invoice_state, "invoiced")

        # The Picking wizard must skip this picking: no new Invoice
        with self.assertRaises(exceptions.UserError):
            create_with_form_inv_onshipping(self.env, picking)
        self.assertEqual(sale_order.invoice_count, 1)

        # 4) Partial delivery with a backorder: both Pickings get invoiced
        sale_order = self._create_confirmed_sale_order(qty=10.0)
        picking = sale_order.picking_ids
        picking.action_confirm()
        picking.action_assign()

        # Partially deliver 6, creating a backorder for 4
        picking.move_ids.quantity = 6.0
        backorder = create_with_form_pck_backorder(self.env, picking)
        self.assertEqual(picking.state, "done")
        self.assertNotEqual(backorder.state, "done")

        # Invoice the full 10 (ordered) from the SO
        sale_order._create_invoices(final=True)
        self.assertEqual(sale_order.invoice_count, 1)

        # Both the delivered picking and the backorder must be invoiced
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(backorder.invoice_state, "invoiced")

    def test_12_both_backorder_invoice_from_so_then_wizard(self):
        """
        'both' policy, realistic partial scenario using a backorder:
        - Deliver 6 of 10, creating a backorder for the remaining 4.
        - Invoice the 6 delivered from the SO: the first picking must be
          marked invoiced, the backorder must stay '2binvoiced'.
        - Deliver and invoice the backorder from the picking wizard:
          quantity must be 4 (remaining on the sale line).
        """
        product = self.product_storable_1
        sale_order = self._create_confirmed_sale_order(
            qty=10.0, invoice_policy="delivery", product=product
        )
        picking = sale_order.picking_ids
        picking.action_confirm()
        picking.action_assign()
        # Deliver 6 out of 10 → backorder for the remaining 4
        picking.move_ids.quantity = 6.0
        backorder = create_with_form_pck_backorder(self.env, picking)
        self.assertEqual(picking.state, "done")
        self.assertNotEqual(backorder.state, "done")

        # Invoice the 6 delivered from the SO
        sale_order._create_invoices(final=True)
        self.assertEqual(sale_order.invoice_count, 1)

        # First picking fully invoiced; backorder still pending
        self.assertEqual(picking.invoice_state, "invoiced")
        self.assertEqual(backorder.invoice_state, "2binvoiced")

        # Deliver the backorder
        self.picking_move_state(backorder)
        self.assertEqual(backorder.state, "done")

        sol = sale_order.order_line.filtered(lambda ln: ln.product_id == product)
        self.assertEqual(sol.qty_to_invoice, 4.0)

        # Invoice the backorder from the picking wizard — should cap to 4
        backorder_invoice = create_with_form_inv_onshipping(self.env, backorder)
        inv_line = backorder_invoice.invoice_line_ids.filtered(
            lambda ln: ln.product_id == product
        )
        self.assertEqual(inv_line.quantity, 4.0)
        self.assertEqual(backorder.invoice_state, "invoiced")
        self.assertEqual(sol.qty_to_invoice, 0.0)

    def test_13_values_from_sale_in_invoice_created_from_picking(self):
        """The Invoice created from the Stock Picking must get the values
        coming from Sale.

        The module reuses the `_prepare_invoice` and `_prepare_invoice_line`
        methods to build the Invoice created from the Picking the same way the
        Invoice created from the Sale Order is built, in order to avoid the
        necessity of 'glue modules': any field added by another module in the
        values used to create the Invoice from Sale (e.g. account_payment_sale,
        sale_commission) must be also informed when the Invoice is created from
        the Picking.
        """
        self.company.sale_invoicing_policy = "both"
        product = self.product_storable_1
        sale_order = self._create_confirmed_sale_order(qty=2.0, product=product)
        picking = sale_order.picking_ids
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        wizard = self.env["stock.invoice.onshipping"]

        # Invoice: fields got from Sale, the ones the module gets from the
        # Picking are informed in `_get_fields_not_used_from_sale`
        not_used = wizard._get_fields_not_used_from_sale() | {"sequence"}
        self._check_values_from_sale(
            invoice,
            sale_order._prepare_invoice(),
            not_used,
            "Field %s from 'sale.order._prepare_invoice' is missing in the "
            "Invoice created from the Stock Picking",
        )

        # Invoice Lines
        sale_line = sale_order.order_line.filtered(lambda ln: ln.product_id == product)
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda ln: ln.product_id == product
        )
        self.assertTrue(invoice_line, "Invoice Line was not created.")
        not_used_line = wizard._get_fields_not_used_from_sale_line() | {"sequence"}
        self._check_values_from_sale(
            invoice_line,
            sale_line._prepare_invoice_line(),
            not_used_line,
            "Field %s from 'sale.order.line._prepare_invoice_line' is missing "
            "in the Invoice Line created from the Stock Picking",
        )

    def test_14_sale_order_policy_keeps_native_behaviour(self):
        """'sale_order' policy: the native behaviour is kept.

        The Stock Moves of a Picking created from a Sale Order are not informed
        as 'to be invoiced' and the Invoice is created from the Sale Order
        without any restriction.
        """
        sale_order = self._create_confirmed_sale_order(policy="sale_order")
        picking = sale_order.picking_ids
        self.assertEqual(picking.invoice_state, "none")
        for move in picking.move_ids:
            self.assertEqual(move.invoice_state, "none")

        # Invoice created from Sale Order, native behaviour
        invoice = sale_order._create_invoices(final=True)
        self.assertEqual(sale_order.invoice_count, 1)
        self.assertEqual(invoice.invoice_origin, sale_order.name)
        self.assertEqual(picking.invoice_state, "none")

    def test_15_invoice_price_from_sale_order_line(self):
        """The price informed in the Sale Order Line has priority in the
        Invoice created from the Picking, see
        `stock.move._get_price_unit_invoice`.
        """
        product = self.product_storable_1
        sale_order = self._create_confirmed_sale_order(
            product=product, policy="stock_picking"
        )
        picking = sale_order.picking_ids
        # Price changed after the confirmation, the Stock Move keeps the
        # original one
        new_price = sale_order.order_line.price_unit + 1000
        sale_order.order_line.write({"price_unit": new_price})
        self.assertNotEqual(picking.move_ids.price_unit, new_price)

        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda ln: ln.product_id == product
        )
        self.assertEqual(invoice_line.price_unit, new_price)

    def test_16_both_wizard_caps_quantity_to_remaining(self):
        """'both' policy: the Picking wizard caps the quantity to what is still
        to invoice in the Sale Order Line, to prevent double invoicing.
        """
        product = self.product_storable_1
        sale_order = self._create_confirmed_sale_order(
            qty=10.0, invoice_policy="delivery", product=product
        )
        picking = sale_order.picking_ids
        picking.action_confirm()
        picking.action_assign()
        # Deliver 6 of 10, backorder for the 4 left
        picking.move_ids.quantity = 6.0
        backorder = create_with_form_pck_backorder(self.env, picking)
        self.assertEqual(picking.state, "done")

        # The 6 delivered are invoiced from the Sale Order
        sale_order._create_invoices(final=True)
        sale_line = sale_order.order_line.filtered(lambda ln: ln.product_id == product)
        self.assertEqual(sale_line.qty_invoiced, 6.0)
        self.assertEqual(picking.invoice_state, "invoiced")

        # Then the 4 left are delivered, 4 left to invoice in the Sale Line
        self.picking_move_state(backorder)
        self.assertEqual(sale_line.qty_to_invoice, 4.0)

        # The already invoiced Picking is sent again to the wizard (button
        # 'To Be Invoiced'): the quantity of the Picking (6) must be capped to
        # the 4 still to invoice in the Sale Order Line
        picking.set_to_be_invoiced()
        invoices_before = sale_order.invoice_ids
        create_with_form_inv_onshipping(self.env, picking)
        invoice = sale_order.invoice_ids - invoices_before
        self.assertEqual(len(invoice), 1)
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda ln: ln.product_id == product
        )
        self.assertEqual(invoice_line.quantity, 4.0)
        self.assertEqual(sale_line.qty_invoiced, 10.0)
        self.assertEqual(sale_line.qty_to_invoice, 0.0)

    def test_17_invoice_with_move_not_linked_to_sale_order(self):
        """A Picking created from a Sale Order with an extra Stock Move (not
        linked to the Sale Order) is invoiced with both lines.
        """
        product = self.product_storable_2
        sale_order = self._create_confirmed_sale_order(policy="stock_picking")
        picking = sale_order.picking_ids
        extra_move = self.env["stock.move"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": 1.0,
                "product_uom": product.uom_id.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "company_id": picking.company_id.id,
            }
        )
        extra_move._set_as_2binvoiced()
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        invoice_lines = invoice.invoice_line_ids.filtered(lambda ln: ln.product_id)
        self.assertEqual(len(invoice_lines), 2)
        self.assertIn(product, invoice_lines.mapped("product_id"))

    def test_18_wizard_without_deduct_down_payments(self):
        """Test the 'Deduct down payments' option disabled.

        The Invoice created from the Picking keeps the Down Payment lines and
        is kept as an Invoice (not switched to a refund) even when the
        deduction of the Down Payments gives it a negative total, while the
        default option switches the same Invoice to a refund.
        """
        # Option disabled: the Invoice stays an Invoice with a negative total
        invoice = self._invoice_from_picking_with_advance(deduct_down_payments=False)
        self.assertLess(invoice.amount_total, 0)
        self.assertEqual(invoice.move_type, "out_invoice")

        # Same case with the option enabled (default): switched to a refund
        refund = self._invoice_from_picking_with_advance(deduct_down_payments=True)
        self.assertEqual(refund.move_type, "out_refund")
        self.assertAlmostEqual(-refund.amount_total, invoice.amount_total, 2)

    def test_19_consumable_product_invoicing_from_picking(self):
        """
        Test that consumable (non-storable) products generate a picking
        and must be invoiced from it, not from the sale order.
        """
        so = self.sale_order_6
        so.action_confirm()
        self.assertTrue(so.picking_ids, "Consumable product should generate a picking")

        # Invoicing from SO must raise error — consumable is not a service
        with self.assertRaises(exceptions.UserError):
            so._create_invoices(final=True)

        # Validate picking and invoice from it
        picking = so.picking_ids
        picking.set_to_be_invoiced()
        self.picking_move_state(picking)

        invoice = create_with_form_inv_onshipping(self.env, picking)
        self.assertEqual(len(invoice), 1)
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
