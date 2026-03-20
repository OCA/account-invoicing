# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions, models
from odoo.tests import Form

from odoo.addons.stock_picking_invoicing.tests.tools import (
    create_with_form_inv_onshipping,
    create_with_form_return_picking,
)

from .common import TestSaleStockPickingInvoicingCommon
from .tools import (
    create_with_form_account_payment,
    create_with_form_sale_adv_pay_inv,
)


class TestSaleStockPickingInvoicing(TestSaleStockPickingInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_sale_stock_return(self):
        """
        Test a SO with a product invoiced on delivery. Deliver and invoice
        the SO, then do a return of the picking. Check that a refund
         invoice is well generated.
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

        sm_fields = [key for key in self.env["stock.move"]._fields.keys()]
        sol_fields = [key for key in self.env["sale.order.line"]._fields.keys()]

        skipped_fields = [
            "id",
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
        common_fields = list(set(sm_fields) & set(sol_fields) - set(skipped_fields))

        for field in common_fields:
            self.assertEqual(
                stock_move[field],
                sale_order_line[field],
                f"Field {field} failed to transfer from sale.order.line "
                "to stock.move",
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

        # Check if the Sale Lines fields are equals to Invoice Lines
        sol_fields = [key for key in self.env["sale.order.line"]._fields.keys()]

        acl_fields = [key for key in self.env["account.move.line"]._fields.keys()]

        skipped_fields = [
            "id",
            "display_name",
            "state",
            "create_date",
            # By th TAX 15% automatic add in invoice the value change
            "price_total",
            # Necessary after call onchange_partner_id
            "write_date",
            "__last_update",
            # Field sequence add in creation of Invoice
            "sequence",
            # In the sale.orde.line display_type has only line_section
            # and line_note, the acccount.move.line has more options
            "display_type",
        ]

        common_fields = list(set(acl_fields) & set(sol_fields) - set(skipped_fields))
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

        picking = sale_order_1.picking_ids
        self.picking_move_state(picking)
        invoice = create_with_form_inv_onshipping(self.env, picking)
        # 2 Products, 2 Down Payment, 1 Note and 1 Section
        self.assertEqual(len(invoice.invoice_line_ids), 6)
        line_section = invoice.invoice_line_ids.filtered(
            lambda line: line.display_type == "line_section"
        )
        assert line_section, "Invoice without Line Section for Down Payment."
        down_payment_line = invoice.invoice_line_ids.filtered(
            lambda line: line.sale_line_ids.is_downpayment
        )
        assert down_payment_line, "Invoice without Down Payment line."

    def test_06_default_value_sale_invoicing_policy(self):
        """Test default value for sale_invoicing_policy"""
        company = self.env["res.company"].create(
            {
                "name": "Test",
            }
        )
        self.assertEqual(company.sale_invoicing_policy, "sale_order")

    def test_07_picking_invocing_without_sale_order(self):
        """Test Picking Invoicing without Sale Order"""
        picking = self.picking_out_1
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
                lambda ln: ln.display_type == "line_section"
                and ln.name == self.product_combo.name
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
                lambda ln: ln.display_type == "line_section"
                and ln.name == self.product_combo.name
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
