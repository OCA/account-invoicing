# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceMerge(AccountTestInvoicingCommon):
    """
    Tests for Account Invoice Merge.
    """

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.company = cls.company_data_2["company"]
        invoice_date = fields.Date.today()
        cls.invoice1 = cls.init_invoice(
            "out_invoice",
            partner=cls.partner_a,
            invoice_date=invoice_date,
            products=cls.product_a,
        )
        cls.now = cls.invoice1.create_date
        cls.invoice2 = cls.init_invoice(
            "out_invoice",
            partner=cls.partner_a,
            invoice_date=invoice_date,
            products=cls.product_a,
        )
        cls.invoice3 = cls.init_invoice(
            "out_invoice",
            partner=cls.partner_b,
            invoice_date=invoice_date,
            products=cls.product_a,
        )
        cls.invoice4 = cls.init_invoice(
            "in_invoice",
            partner=cls.partner_a,
            invoice_date=invoice_date,
            products=cls.product_a,
        )
        cls.invoice5 = cls.init_invoice(
            "out_invoice",
            partner=cls.partner_a,
            invoice_date=invoice_date,
            products=cls.product_a,
        )
        cls.invoice6 = cls.init_invoice(
            "out_invoice",
            partner=cls.partner_a,
            products=cls.product_a,
            invoice_date=invoice_date,
            company=cls.company,
        )

        cls.inv_model = cls.env["account.move"]
        cls.wiz = cls.env["invoice.merge"]

    def _get_wizard(self, active_ids, create=False):
        wiz = self.wiz.with_context(
            active_ids=active_ids,
            active_model="account.move",
        )
        if create:
            wiz = wiz.create({})
        return wiz

    def test_invoice_merge(self):
        self.assertEqual(len(self.invoice1.invoice_line_ids), 1)
        self.assertEqual(len(self.invoice2.invoice_line_ids), 1)
        invoice_len_args = [
            ("create_date", ">=", self.now),
            ("partner_id", "=", self.partner_a.id),
            ("state", "=", "draft"),
        ]
        start_inv = self.inv_model.search(invoice_len_args)
        self.assertEqual(len(start_inv), 5)

        wiz = self._get_wizard([self.invoice1.id, self.invoice2.id], create=True)
        action = wiz.merge_invoices()

        self.assertLessEqual(
            {
                "type": "ir.actions.act_window",
                "binding_view_types": "list,form",
                "xml_id": "account.action_move_out_invoice_type",
            }.items(),
            action.items(),
            "There was an error and the two invoices were not merged.",
        )

        end_inv = self.inv_model.search(invoice_len_args)
        self.assertEqual(len(end_inv), 4)
        self.assertEqual(len(end_inv[0].invoice_line_ids), 1)
        self.assertEqual(end_inv[0].invoice_line_ids[0].quantity, 2.0)

    def test_error_check(self):
        """Check"""
        # Different partner
        wiz = self._get_wizard([self.invoice1.id, self.invoice3.id], create=True)
        self.assertEqual(
            wiz.error_message, "All invoices must have the same: \n- Partner"
        )

        # Check with only one invoice
        wiz = self._get_wizard([self.invoice1.id], create=True)
        self.assertEqual(
            wiz.error_message,
            "Please select multiple invoices to merge in the list view.",
        )

        # Check with two different invoice type
        wiz = self._get_wizard([self.invoice1.id, self.invoice4.id], create=True)
        self.assertEqual(
            wiz.error_message, "All invoices must have the same: \n- Type\n- Journal"
        )

        # Check with a canceled invoice
        self.invoice5.button_cancel()
        wiz = self._get_wizard([self.invoice1.id, self.invoice5.id], create=True)
        self.assertEqual(
            wiz.error_message,
            "All invoices must have the same: \n- Merge-able State (ex : Draft)",
        )

        # Check with another company
        wiz = self._get_wizard([self.invoice1.id, self.invoice6.id], create=True)
        self.assertEqual(
            wiz.error_message, "All invoices must have the same: \n- Journal\n- Company"
        )

    def test_callback_different_sale_order_00(self):
        if "sale.order" not in self.env.registry:
            return True
        product_1, product_2 = self.env["product.product"].create(
            [
                {
                    "name": "product 1",
                    "list_price": 5.0,
                },
                {
                    "name": "product 2",
                    "list_price": 10.0,
                },
            ]
        )
        # Test pre-computes of lines with order
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Dummy section",
                        }
                    ),
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Dummy section",
                        }
                    ),
                    Command.create(
                        {
                            "product_id": product_1.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": product_2.id,
                        }
                    ),
                ],
            }
        )
        sale_order_2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Dummy section",
                        }
                    ),
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Dummy section",
                        }
                    ),
                    Command.create(
                        {
                            "product_id": product_1.id,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": product_2.id,
                        }
                    ),
                ],
            }
        )
        sale_order.action_confirm()
        sale_order._create_invoices(final=True)
        sale_order_2.action_confirm()
        sale_order_2._create_invoices(final=True)
        invoices = (sale_order | sale_order_2).mapped(
            "order_line.invoice_lines.move_id"
        )
        invoices_info = invoices.do_merge(
            keep_references=False, date_invoice=fields.Date.today()
        )
        invoices_2 = (sale_order | sale_order_2).mapped(
            "order_line.invoice_lines.move_id"
        )
        invoices_2 = invoices_2.filtered(lambda i: i.state == "draft")
        self.assertEqual(sorted(invoices_2.ids), sorted(list(invoices_info.keys())))

    def _add_qty_delivered_and_create_invoice(self, sale_order):
        for line in sale_order.order_line:
            if line.qty_delivered < line.product_uom_qty:
                line.qty_delivered += 1
        sale_order._create_invoices(final=True)

    def _add_qty_received_and_create_invoice(self, purchase_order):
        for line in purchase_order.order_line:
            if line.qty_received < line.product_qty:
                line.qty_received += 1
        purchase_order.action_create_invoice()

    def test_callback_different_sale_order_01(self):
        if "sale.order" not in self.env.registry:
            return True
        product_1, product_2 = self.env["product.product"].create(
            [
                {"name": "product 1", "list_price": 5.0, "invoice_policy": "delivery"},
                {"name": "product 2", "list_price": 10.0, "invoice_policy": "delivery"},
            ]
        )
        # Test pre-computes of lines with order
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    Command.create({"product_id": product_1.id, "product_uom_qty": 5}),
                    Command.create({"product_id": product_2.id, "product_uom_qty": 5}),
                ],
            }
        )
        sale_order_2 = sale_order.copy()

        sale_order.action_confirm()
        sale_order_2.action_confirm()

        self._add_qty_delivered_and_create_invoice(sale_order)
        self._add_qty_delivered_and_create_invoice(sale_order)
        self._add_qty_delivered_and_create_invoice(sale_order)
        self._add_qty_delivered_and_create_invoice(sale_order_2)
        self._add_qty_delivered_and_create_invoice(sale_order_2)
        self._add_qty_delivered_and_create_invoice(sale_order_2)

        inv_sale_order = sale_order.mapped("order_line.invoice_lines.move_id")
        inv_sale_order_2 = sale_order_2.mapped("order_line.invoice_lines.move_id")
        total_inv_sale_order = inv_sale_order | inv_sale_order_2

        self.assertEqual(len(inv_sale_order), 3)
        self.assertEqual(len(inv_sale_order_2), 3)
        self.assertEqual(len(total_inv_sale_order), 6)
        for line in sale_order.order_line:
            self.assertEqual(line.qty_delivered, 3)
            self.assertEqual(line.qty_invoiced, 3)
        for line in sale_order_2.order_line:
            self.assertEqual(line.qty_delivered, 3)
            self.assertEqual(line.qty_invoiced, 3)

        invoices = (
            sale_order.mapped("order_line.invoice_lines.move_id")[:1]
            | sale_order_2.mapped("order_line.invoice_lines.move_id")[:1]
        )
        invoices.do_merge(keep_references=False, date_invoice=fields.Date.today())

        inv_sale_order = sale_order.mapped("order_line.invoice_lines.move_id")
        inv_sale_order_2 = sale_order_2.mapped("order_line.invoice_lines.move_id")
        total_inv_sale_order = inv_sale_order | inv_sale_order_2

        self.assertEqual(len(inv_sale_order), 3)
        self.assertEqual(len(inv_sale_order_2), 3)
        self.assertEqual(len(total_inv_sale_order), 5)
        for line in sale_order.order_line:
            self.assertEqual(line.qty_delivered, 3)
            self.assertEqual(line.qty_invoiced, 3)
        for line in sale_order_2.order_line:
            self.assertEqual(line.qty_delivered, 3)
            self.assertEqual(line.qty_invoiced, 3)

    def test_callback_same_sale_order(self):
        if "sale.order" not in self.env.registry:
            return True
        product_1, product_2 = self.env["product.product"].create(
            [
                {"name": "product 1", "list_price": 5.0, "invoice_policy": "delivery"},
                {"name": "product 2", "list_price": 10.0, "invoice_policy": "delivery"},
            ]
        )
        # Test pre-computes of lines with order
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    Command.create({"product_id": product_1.id, "product_uom_qty": 5}),
                    Command.create({"product_id": product_2.id, "product_uom_qty": 5}),
                ],
            }
        )

        sale_order.action_confirm()
        self._add_qty_delivered_and_create_invoice(sale_order)
        self._add_qty_delivered_and_create_invoice(sale_order)
        self._add_qty_delivered_and_create_invoice(sale_order)
        self._add_qty_delivered_and_create_invoice(sale_order)
        self._add_qty_delivered_and_create_invoice(sale_order)

        invoices = sale_order.mapped("order_line.invoice_lines.move_id")
        invoices[-1].button_cancel()
        invoices[-2].action_post()

        self.assertEqual(len(invoices), 5)
        for line in sale_order.order_line:
            self.assertEqual(line.qty_delivered, 5)
            self.assertEqual(line.qty_invoiced, 4)

        invoices[:2].do_merge(keep_references=False)

        invoices = sale_order.mapped("order_line.invoice_lines.move_id")

        self.assertEqual(len(invoices), 4)
        for line in sale_order.order_line:
            self.assertEqual(line.qty_delivered, 5)
            self.assertEqual(line.qty_invoiced, 4)

    def test_callback_different_purchase_order(self):
        if "purchase.order" not in self.env.registry:
            return True
        product_1, product_2 = self.env["product.product"].create(
            [
                {"name": "product 1", "list_price": 5.0, "invoice_policy": "delivery"},
                {"name": "product 2", "list_price": 10.0, "invoice_policy": "delivery"},
            ]
        )
        # Test pre-computes of lines with order
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    Command.create({"product_id": product_1.id, "product_qty": 5}),
                    Command.create({"product_id": product_2.id, "product_qty": 5}),
                ],
            }
        )
        purchase_order_2 = purchase_order.copy()

        purchase_order.button_confirm()
        purchase_order_2.button_confirm()

        self._add_qty_received_and_create_invoice(purchase_order)
        self._add_qty_received_and_create_invoice(purchase_order)
        self._add_qty_received_and_create_invoice(purchase_order)
        self._add_qty_received_and_create_invoice(purchase_order_2)
        self._add_qty_received_and_create_invoice(purchase_order_2)
        self._add_qty_received_and_create_invoice(purchase_order_2)

        inv_purchase_order = purchase_order.mapped("order_line.invoice_lines.move_id")
        inv_purchase_order_2 = purchase_order_2.mapped(
            "order_line.invoice_lines.move_id"
        )
        total_inv_purchase_order = inv_purchase_order | inv_purchase_order_2

        self.assertEqual(len(inv_purchase_order), 3)
        self.assertEqual(len(inv_purchase_order_2), 3)
        self.assertEqual(len(total_inv_purchase_order), 6)
        for line in purchase_order.order_line:
            self.assertEqual(line.qty_received, 3)
            self.assertEqual(line.qty_invoiced, 3)
        for line in purchase_order_2.order_line:
            self.assertEqual(line.qty_received, 3)
            self.assertEqual(line.qty_invoiced, 3)

        invoices = inv_purchase_order[:1] | inv_purchase_order_2[:1]
        invoices[:2].do_merge(keep_references=False)

        inv_purchase_order = purchase_order.mapped("order_line.invoice_lines.move_id")
        inv_purchase_order_2 = purchase_order_2.mapped(
            "order_line.invoice_lines.move_id"
        )
        total_inv_purchase_order = inv_purchase_order | inv_purchase_order_2

        self.assertEqual(len(inv_purchase_order), 3)
        self.assertEqual(len(inv_purchase_order_2), 3)
        self.assertEqual(len(total_inv_purchase_order), 5)
        for line in purchase_order.order_line:
            self.assertEqual(line.qty_received, 3)
            self.assertEqual(line.qty_invoiced, 3)
        for line in purchase_order_2.order_line:
            self.assertEqual(line.qty_received, 3)
            self.assertEqual(line.qty_invoiced, 3)

    def test_callback_same_purchase_order(self):
        if "purchase.order" not in self.env.registry:
            return True
        product_1, product_2 = self.env["product.product"].create(
            [
                {"name": "product 1", "list_price": 5.0, "invoice_policy": "delivery"},
                {"name": "product 2", "list_price": 10.0, "invoice_policy": "delivery"},
            ]
        )
        # Test pre-computes of lines with order
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [
                    Command.create({"product_id": product_1.id, "product_qty": 5}),
                    Command.create({"product_id": product_2.id, "product_qty": 5}),
                ],
            }
        )

        purchase_order.button_confirm()
        self._add_qty_received_and_create_invoice(purchase_order)
        self._add_qty_received_and_create_invoice(purchase_order)
        self._add_qty_received_and_create_invoice(purchase_order)
        self._add_qty_received_and_create_invoice(purchase_order)
        self._add_qty_received_and_create_invoice(purchase_order)

        invoices = purchase_order.mapped("order_line.invoice_lines.move_id")
        invoices[-1].button_cancel()
        invoices[-2].write({"invoice_date": fields.Date.today()})
        invoices[-2].action_post()

        self.assertEqual(len(invoices), 5)
        for line in purchase_order.order_line:
            self.assertEqual(line.qty_received, 5)
            self.assertEqual(line.qty_invoiced, 4)

        invoices[:2].do_merge(keep_references=False)

        invoices = purchase_order.mapped("order_line.invoice_lines.move_id")

        self.assertEqual(len(invoices), 4)
        for line in purchase_order.order_line:
            self.assertEqual(line.qty_received, 5)
            self.assertEqual(line.qty_invoiced, 4)
