# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSplitInvoice(TransactionCase):

    def test_split_invoice_from_sale_order(self):
        sale_order = self.env.ref("sale.sale_order_8")
        sale_order.order_line.mapped("product_id").write(
            {"invoice_policy": "order"}
        )
        sale_order.action_confirm()
        sale_order.action_invoice_create()
        invoice = sale_order.invoice_ids
        line_0 = invoice.invoice_line_ids[0]
        line_1 = invoice.invoice_line_ids[1]

        self.assertEquals(line_0.sale_line_ids.order_id, sale_order)
        self.assertEquals(line_1.sale_line_ids.order_id, sale_order)

        line_1.split = True
        invoice.btn_split_quotation()
        split_invoice = self.env["account.invoice"].search(
            [("split_id", "=", invoice.id)]
        )

        self.assertEquals(len(invoice.invoice_line_ids), 1)
        self.assertEquals(
            invoice.invoice_line_ids.sale_line_ids.order_id, sale_order
        )

        self.assertEquals(len(split_invoice.invoice_line_ids), 1)
        self.assertEquals(
            split_invoice.invoice_line_ids.sale_line_ids.order_id, sale_order
        )
