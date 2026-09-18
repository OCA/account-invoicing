# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

# TODO: In v16 check the possiblity to use the commom.py
# from stock_picking_invoicing
# https://github.com/OCA/account-invoicing/blob/16.0/
# stock_picking_invoicing/tests/common.py
from odoo.tests import Form, TransactionCase


class TestSaleStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_move_model = cls.env["account.move"]
        cls.invoice_wizard = cls.env["stock.invoice.onshipping"]
        cls.stock_return_picking = cls.env["stock.return.picking"]
        cls.stock_picking = cls.env["stock.picking"]
        # In order to avoid errors in the tests CI environment when the tests
        # Create of Invoice by Sale Order using sale.advance.payment.inv object
        # is necessary let default policy as sale_order, just affect demo data.
        # TODO: Is there other form to avoid this problem?
        cls.companies = cls.env["res.company"].search(
            [("sale_invoicing_policy", "=", "sale_order")]
        )
        for company in cls.companies:
            company.sale_invoicing_policy = "stock_picking"

    def _run_picking_onchanges(self, record):
        record.onchange_partner_id()

    def _run_line_onchanges(self, record):
        record._onchange_product_id()

    def picking_move_state(self, picking):
        self._run_picking_onchanges(picking)
        picking.action_confirm()
        # Check product availability
        picking.action_assign()
        # Force product availability
        for move in picking.move_ids_without_package:
            self._run_line_onchanges(move)
            move.quantity_done = move.product_uom_qty
        picking.button_validate()

    def create_invoice_wizard(self, pickings):
        wizard_obj = self.env["stock.invoice.onshipping"].with_context(
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
        domain = [("picking_ids", "in", pickings.ids)]
        invoice = self.env["account.move"].search(domain)
        return invoice

    def return_picking_wizard(self, picking):
        # Return Picking
        return_wizard_form = Form(
            self.env["stock.return.picking"].with_context(
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
        return picking_devolution

    def test_01_sale_stock_return(self):
        """
        Test a SO with a product invoiced on delivery. Deliver and invoice
        the SO, then do a return of the picking. Check that a refund
         invoice is well generated.
        """
        # intial so
        self.partner = self.env.ref(
            "sale_stock_picking_invoicing.res_partner_2_address"
        )
        self.product = self.env.ref("product.product_delivery_01")
        so_vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": self.product.id,
                        "product_uom_qty": 3.0,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
        }
        self.so = self.env["sale.order"].create(so_vals)

        # confirm our standard so, check the picking
        self.so.action_confirm()
        self.assertTrue(
            self.so.picking_ids,
            'Sale Stock: no picking created for "invoice on '
            'delivery" storable products',
        )

        # set stock.picking to be invoiced
        self.assertTrue(
            len(self.so.picking_ids) == 1,
            "More than one stock " "picking for sale.order",
        )
        self.so.picking_ids.set_to_be_invoiced()

        # validate stock.picking
        stock_picking = self.so.picking_ids

        # compare sale.order.line with stock.move
        stock_move = stock_picking.move_lines
        sale_order_line = self.so.order_line

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
                "Field %s failed to transfer from "
                "sale.order.line to stock.move" % field,
            )

    def test_picking_sale_order_product_and_service(self):
        """
        Test Sale Order with product and service
        """

        sale_order_2 = self.env.ref(
            "sale_stock_picking_invoicing.main_company-sale_order_2"
        )
        # Necessary to get the currency
        sale_order_2.onchange_partner_id()
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

        invoice = self.create_invoice_wizard(picking)
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
            lambda ln: ln.product_id.type == "product"
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
        ]

        common_fields = list(set(acl_fields) & set(sol_fields) - set(skipped_fields))
        sale_order_line = picking.move_ids_without_package.filtered(
            lambda ln: ln.sale_line_id
        ).sale_line_id
        invoice_lines = picking.invoice_ids.invoice_line_ids.filtered(
            lambda ln: ln.product_id
        )

        for field in common_fields:
            self.assertEqual(
                sale_order_line[field],
                invoice_lines[field],
                "Field %s failed to transfer from "
                "sale.order.line to account.invoice.line" % field,
            )

        # Return Picking
        picking_devolution = self.return_picking_wizard(picking)

        self.assertEqual(picking_devolution.invoice_state, "2binvoiced")
        for line in picking_devolution.move_lines:
            self.assertEqual(line.invoice_state, "2binvoiced")

        self.picking_move_state(picking_devolution)
        self.assertEqual(picking_devolution.state, "done", "Change state fail.")

        invoice_devolution = self.create_invoice_wizard(picking_devolution)
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

    def test_picking_invoicing_partner_shipping_invoiced(self):
        """
        Test the invoice generation grouped by partner/product with 2
        picking and 2 moves per picking, but Partner to Shipping is
        different from Partner to Invoice.
        """
        sale_order_1 = self.env.ref(
            "sale_stock_picking_invoicing.main_company-sale_order_1"
        )
        sale_order_1.action_confirm()
        picking = sale_order_1.picking_ids
        self.picking_move_state(picking)
        sale_order_2 = self.env.ref(
            "sale_stock_picking_invoicing.main_company-sale_order_2"
        )
        sale_order_2.action_confirm()
        picking2 = sale_order_2.picking_ids
        self.picking_move_state(picking2)
        pickings = picking | picking2
        invoice = self.create_invoice_wizard(pickings)
        # Groupping Invoice
        self.assertEqual(len(invoice), 1)
        # Invoice should be create with the partner_invoice_id
        self.assertEqual(invoice.partner_id, sale_order_1.partner_invoice_id)
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

    def test_ungrouping_pickings_partner_shipping_different(self):
        """
        Test the invoice generation grouped by partner/product with 3
        picking and 2 moves per picking, the 3 has the same Partner to
        Invoice but one has Partner to Shipping so shouldn't be grouping.
        """

        sale_order_1 = self.env.ref(
            "sale_stock_picking_invoicing.main_company-sale_order_1"
        )
        sale_order_1.action_confirm()
        picking = sale_order_1.picking_ids
        self.picking_move_state(picking)

        sale_order_3 = self.env.ref(
            "sale_stock_picking_invoicing.main_company-sale_order_3"
        )
        sale_order_3.action_confirm()
        picking3 = sale_order_3.picking_ids
        self.picking_move_state(picking3)

        sale_order_4 = self.env.ref(
            "sale_stock_picking_invoicing.main_company-sale_order_4"
        )
        sale_order_4.action_confirm()
        picking4 = sale_order_4.picking_ids
        self.picking_move_state(picking4)

        pickings = picking | picking3 | picking4
        invoices = self.create_invoice_wizard(pickings)
        # Even with same Partner Invoice if the Partner Shipping
        # are different should not be Groupping
        self.assertEqual(len(invoices), 2)

        # Invoice that has different Partner Shipping
        # should be not groupping
        invoice_pick_1 = invoices.filtered(
            lambda t: t.partner_id != t.partner_shipping_id
        )
        # Invoice should be create with partner_invoice_id
        self.assertEqual(invoice_pick_1.partner_id, sale_order_1.partner_invoice_id)
        # Invoice create with Partner Shipping used in Picking
        self.assertEqual(invoice_pick_1.partner_shipping_id, picking.partner_id)

        # Groupping Invoice
        invoice_pick_3_4 = invoices.filtered(
            lambda t: t.partner_id == t.partner_shipping_id
        )
        self.assertIn(invoice_pick_3_4, picking3.invoice_ids)
        self.assertIn(invoice_pick_3_4, picking4.invoice_ids)

    def test_down_payment(self):
        """Test the case with Down Payment"""
        sale_order_1 = self.env.ref(
            "sale_stock_picking_invoicing.main_company-sale_order_1"
        )
        sale_order_1.action_confirm()
        # Create Invoice Sale
        context = {
            "active_model": "sale.order",
            "active_id": sale_order_1.id,
            "active_ids": sale_order_1.ids,
        }
        # DownPayment
        payment_wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(**context)
            .create(
                {
                    "advance_payment_method": "percentage",
                    "amount": 50,
                }
            )
        )
        payment_wizard.create_invoices()

        invoice_down_payment = sale_order_1.invoice_ids[0]
        invoice_down_payment.action_post()
        payment_register = Form(
            self.env["account.payment.register"].with_context(
                active_model="account.move",
                active_ids=invoice_down_payment.ids,
            )
        )
        journal_cash = self.env["account.journal"].search(
            [
                ("type", "=", "cash"),
                ("company_id", "=", invoice_down_payment.company_id.id),
            ],
            limit=1,
        )
        payment_register.journal_id = journal_cash
        payment_register.amount = invoice_down_payment.amount_total
        payment_register.save()._create_payments()

        picking = sale_order_1.picking_ids
        self.picking_move_state(picking)
        invoice = self.create_invoice_wizard(picking)
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

    def test_default_value_sale_invoicing_policy(self):
        """Test default value for sale_invoicing_policy"""
        company = self.env["res.company"].create(
            {
                "name": "Test",
            }
        )
        self.assertEqual(company.sale_invoicing_policy, "sale_order")

    def test_picking_invocing_without_sale_order(self):
        """Test Picking Invoicing without Sale Order"""
        picking = self.env.ref("stock_picking_invoicing.stock_picking_invoicing_1")
        self.picking_move_state(picking)
        invoice = self.create_invoice_wizard(picking)
        self.assertEqual(len(invoice), 1)
