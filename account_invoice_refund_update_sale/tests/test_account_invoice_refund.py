# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase
import datetime
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAccountInvoiceRefund(TransactionCase):

    def _create_sale_order_line(self, order, product, qty):
        line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'price_unit': 100,
            })
        line.product_id_change()
        line._convert_to_write(line._cache)
        return line

    def setUp(self):
        super(TestAccountInvoiceRefund, self).setUp()
        self.account_invoice_obj = self.env['account.invoice']
        self.account_obj = self.env['account.account']
        self.journal_obj = self.env['account.journal']
        self.invoice_refund_obj = self.env['account.invoice.refund']
        self.payment_term = self.env.ref('account.account_payment_term_advance')
        self.partner3 = self.env.ref('base.res_partner_3')
        self.account_user_type = self.env.ref('account.data_account_type_receivable')
        self.product_id = self.env.ref('product.product_product_5')
        self.account_revenue = self.env.ref('account.data_account_type_revenue')
        self.product_id.invoice_policy = 'order'
        self.journalrec = self.journal_obj.search([('type', '=', 'sale')])[0]
        self.account_id = self.account_obj.search([
            ('user_type_id', '=', self.account_revenue.id)], limit=1)

        self.account_rec1_id = self.account_obj.create(dict(
            code="cust_acc",
            name="customer account",
            user_type_id=self.account_user_type.id,
            reconcile=True,
        ))
        invoice_line_data = [
            (0, 0,
                {
                    'product_id': self.product_id.id,
                    'quantity': 10.0,
                    'account_id': self.account_id.id,
                    'name': 'product test 5',
                    'price_unit': 100.00,
                }
             )
        ]

        self.account_invoice_customer0 = self.account_invoice_obj.create(dict(
            name="Test Customer Invoice",
            payment_term_id=self.payment_term.id,
            journal_id=self.journalrec.id,
            partner_id=self.partner3.id,
            account_id=self.account_rec1_id.id,
            invoice_line_ids=invoice_line_data
        ))

    def test_invoice_refund_update_sale(self):
        # create invoice directly
        self.account_invoice_customer0.action_invoice_open()
        self.account_invoice_refund_0 = self.invoice_refund_obj.with_context(
            {'active_ids': self.account_invoice_customer0.ids}
        ).create(
            dict(
                description='Credit Note',
                date=datetime.date.today(),
                update_sale_order=True,
                filter_refund='refund')
        )
        res = self.account_invoice_refund_0.invoice_refund()
        new_invoice = self.account_invoice_obj.search(res['domain'])
        self.assertFalse(new_invoice.invoice_line_ids.sale_line_ids)

        # create invoice from sale order
        order1 = self.env['sale.order'].create({
            'partner_id': self.partner3.id,
        })
        self._create_sale_order_line(order1, self.product_id, 5)
        order1.action_confirm()
        self.assertEqual(order1.state, 'sale')
        picking = order1.picking_ids[0]
        picking.action_assign()
        for sml in picking.move_lines:
            sml.quantity_done = sml.product_qty
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        self.sale_invoice_id = order1.action_invoice_create()
        self.sale_invoice = self.account_invoice_obj.browse(self.sale_invoice_id)
        self.sale_invoice.action_invoice_open()
        self.assertAlmostEqual(order1.order_line.qty_invoiced, 5.0)

        self.account_invoice_refund_1 = self.invoice_refund_obj.with_context(
            {'active_ids': self.sale_invoice_id}
        ).create(
            dict(
                description='Credit Note',
                date=datetime.date.today(),
                update_sale_order=True,
                filter_refund='refund')
        )
        res_sale = self.account_invoice_refund_1.invoice_refund()
        new_invoice_sale = self.account_invoice_obj.search(res_sale['domain'])
        self.assertTrue(new_invoice_sale.invoice_line_ids.sale_line_ids)
        self.assertAlmostEqual(order1.order_line.qty_invoiced, 0.0)
