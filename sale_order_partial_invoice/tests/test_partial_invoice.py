# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common
from openerp import netsvc


class TestCrmClaimOperatingUnit(common.TransactionCase):

    def setUp(self):
        super(TestCrmClaimOperatingUnit, self).setUp()
        cr, uid, context = self.cr, self.uid, {}
        data_model = self.registry('ir.model.data')
        self.res_users_model = self.registry('res.users')
        self.product_model = self.registry('product.product')
        self.sale_order_model = self.registry('sale.order')
        self.stock_picking_model = self.registry('stock.picking')
        self.inv_par_model = self.registry('sale.order.line.invoice.partially')
        self.account_invoice_model = self.registry('account.invoice')
        self.account_journal_model = self.registry('account.journal')
        self.procurement_order_model = self.registry('procurement.order')
        self.change_product_qty_model = self.\
            registry('stock.change.product.qty')
        self.partner_id = data_model.get_object(cr, uid, 'base',
                                                'res_partner_2')
        self.pricelist = data_model.get_object(cr, uid, 'product', 'list0')
        self.product_uom_id = data_model.get_object(cr, uid, 'product',
                                                    'product_uom_unit').id
        self.account_cash_id = data_model.get_object(cr, uid,
                                                     'account', 'cash').id
        self.account_period_8_id = data_model.get_object(cr, uid, 'account',
                                                         'period_8').id

        """ Create stockable products for testing purpose"""
        name = 'LCD Projector'
        list_price = 1234.99
        product_type = 'product'
        procure_method = 'make_to_stock'
        self.stockable_product_id = self.\
            _create_product(cr, uid, name, list_price, product_type,
                            procure_method, context=context)
        name = 'LCD Projector 3 Year Warranty'
        list_price = 299.99
        product_type = 'service'
        procure_method = 'make_to_stock'
        self.service_product_id = self.\
            _create_product(cr, uid, name, list_price, product_type,
                            procure_method, context=context)
        name = 'Spare screws'
        list_price = 1.22
        product_type = 'consu'
        procure_method = 'make_to_stock'
        self.consumable_product_id = self.\
            _create_product(cr, uid, name, list_price, product_type,
                            procure_method, context=context)
        wiz_context = {'active_id': self.stockable_product_id}
        wiz_chg_qty_id = self.change_product_qty_model.create(cr, uid, {
            'product_id': self.stockable_product_id,
            'new_quantity': 5})
        self.change_product_qty_model.\
            change_product_qty(cr, uid, [wiz_chg_qty_id],
                               context=wiz_context)

    def _create_product(self, cr, uid, name, list_price, product_type,
                        procure_method, context=None):
        """Create a Product."""
        product_id = self.product_model.create(cr, uid, {
            'name': name,
            'type': product_type,
            'standard_price': 1.0,
            'list_price': list_price,
            'procure_method': procure_method
        })
        return product_id

    def _create_sale_order(self, cr, uid, context):

        """Create a sale order."""
        stockable_lines = {
            'product_id': self.stockable_product_id,
            'product_uom_qty': 3,
            'name': 'Stockable Product'}
        service_lines = {
            'product_id': self.service_product_id,
            'product_uom_qty': 3,
            'name': 'Service Product'}
        consu_lines = {
            'product_id': self.consumable_product_id,
            'product_uom_qty': 12,
            'name': ' Consumable Product'}

        lines = [(0, 0, stockable_lines),
                 (0, 0, service_lines),
                 (0, 0, consu_lines)]

        sale_id = self.sale_order_model.create(cr, uid, {
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'order_policy': 'manual',
            'order_line': lines,
            'pricelist_id': self.pricelist.id,
        }, context=context)

        return sale_id

    def test_security(self):
        cr, uid, context = self.cr, self.uid, {}
        sale_id = self._create_sale_order(cr, uid, context=context)
        sale = self.sale_order_model.browse(cr, uid, sale_id, context=context)

        """ Check qty_invoiced """
        self.assertEqual(sale.order_line[0].qty_invoiced, 0,
                         'qty_invoiced not correctly implemented')
        self.assertEqual(sale.order_line[1].qty_invoiced, 0,
                         'qty_invoiced not correctly implemented')
        self.assertEqual(sale.order_line[2].qty_invoiced, 0,
                         'qty_invoiced not correctly implemented')

        """Check qty_delivered """
        self.assertEqual(sale.order_line[0].qty_delivered, 0,
                         'qty_delivered not correctly implemented')
        self.assertEqual(sale.order_line[1].qty_delivered, 0,
                         'qty_delivered not correctly implemented')
        self.assertEqual(sale.order_line[2].qty_delivered, 0,
                         'qty_delivered not correctly implemented')

        """  Confirm Order """
        sale.action_button_confirm()

        """ Check qty_invoiced """
        self.assertEqual(sale.order_line[0].qty_invoiced, 0,
                         'qty_invoiced not correctly implemented')
        self.assertEqual(sale.order_line[1].qty_invoiced, 0,
                         'qty_invoiced not correctly implemented')
        self.assertEqual(sale.order_line[2].qty_invoiced, 0,
                         'qty_invoiced not correctly implemented')

        """ Check qty_delivered """
        self.assertEqual(sale.order_line[0].qty_delivered, 0,
                         'qty_delivered not correctly implemented')
        self.assertEqual(sale.order_line[1].qty_delivered, 0,
                         'qty_delivered not correctly implemented')
        self.assertEqual(sale.order_line[2].qty_delivered, 0,
                         'qty_delivered not correctly implemented')

        """  Partial delivery """
        delivery_orders = self.stock_picking_model.\
            search(cr, uid, [('sale_id', '=', sale.id)])
        first_picking = self.stock_picking_model.browse(cr, uid,
                                                        delivery_orders[-1],
                                                        context=context)
        if first_picking.force_assign(cr, uid, first_picking):
            self.assertEqual(len(first_picking.move_lines), 2,
                             "wrong count of stock moves")
            partial_moves = {}
            for move in first_picking.move_lines:
                partial_moves['move%s' % move.id] =\
                    {'product_qty': move.product_qty / 3,
                     'product_uom': self.product_uom_id}
            first_picking.do_partial(partial_moves, context=context)
        sale = self.sale_order_model.browse(cr, uid, sale.id)

        """  Check qty_invoiced """
        self.assertEqual(sale.order_line[0].qty_invoiced, 0,
                         'qty_invoiced not correctly implemented')
        self.assertEqual(sale.order_line[1].qty_invoiced, 0,
                         'qty_invoiced not correctly implemented')
        self.assertEqual(sale.order_line[2].qty_invoiced, 0,
                         'qty_invoiced not correctly implemented')

        """  Check qty_delivered """
        self.assertEqual(sale.order_line[0].qty_delivered, 1,
                         'qty_delivered not correctly implemented')
        self.assertEqual(sale.order_line[1].qty_delivered, 0,
                         'qty_delivered not correctly implemented')
        self.assertEqual(sale.order_line[2].qty_delivered, 4,
                         'qty_delivered not correctly implemented')

        """ Check SO state """
        sale = self.sale_order_model.browse(cr, uid, sale.id)
        self.assertEqual(sale.state, 'manual')

        """ Create partial invoice """
        sale = self.sale_order_model.browse(cr, uid, sale.id, context=context)
        wiz_data = {'name': 'wiz1',
                    'line_ids': [(0, 0,
                                  {'sale_order_line_id': sale.order_line[0].id,
                                   'quantity': 1}),
                                 (0, 0,
                                  {'sale_order_line_id': sale.order_line[1].id,
                                   'quantity': 1}),
                                 (0, 0,
                                  {'sale_order_line_id': sale.order_line[2].id,
                                   'quantity': 4}),
                                 ],
                    }
        ids = self.inv_par_model.create(cr, uid, wiz_data, context=context)
        self.inv_par_model.create_invoice(cr, uid, [ids], context=context)

        """ Check the 1st invoice is created """
        sale = self.sale_order_model.browse(cr, uid, sale.id, context=context)
        self.assertEqual(len(sale.invoice_ids), 1, "I should have 1 invoice")

        """ Check qty_invoiced """
        self.assertEqual(sale.order_line[0].qty_invoiced, 1,
                         "qty_invoiced not correctly implemented")
        self.assertEqual(sale.order_line[1].qty_invoiced, 1,
                         "qty_invoiced not correctly implemented")
        self.assertEqual(sale.order_line[2].qty_invoiced, 4,
                         "qty_invoiced not correctly implemented")

        """ Check qty_delivered """
        self.assertEqual(sale.order_line[0].qty_delivered, 1,
                         "qty_delivered not correctly implemented")
        self.assertEqual(sale.order_line[1].qty_delivered, 1,
                         "qty_delivered not correctly implemented")
        self.assertEqual(sale.order_line[2].qty_delivered, 4,
                         "qty_delivered not correctly implemented")

        """ Check SO state """
        sale = self.sale_order_model.browse(cr, uid, sale.id)
        self.assertEqual(sale.state, 'manual')

        """ Partial delivery """
        delivery_orders = self.stock_picking_model.\
            search(cr, uid, [('sale_id', '=', sale.id),
                             ('state', '!=', 'done')])
        picking = self.stock_picking_model.browse(cr, uid, delivery_orders[-1],
                                                  context=context)
        if picking.force_assign(cr, uid, picking):
            self.assertEqual(len(picking.move_lines), 2,
                             "wrong count of stock moves")
            partial_moves = {}
            for move in picking.move_lines:
                partial_moves['move%s' % move.id] =\
                    {'product_qty': move.product_qty,
                     'product_uom': self.product_uom_id}
            picking.do_partial(partial_moves, context=context)

        """  Create partial invoice """
        sale = self.sale_order_model.browse(cr, uid, sale.id, context=context)
        wiz_data = {'name': 'wiz2',
                    'line_ids': [(0, 0,
                                  {'sale_order_line_id': sale.order_line[0].id,
                                   'quantity': 2}),
                                 (0, 0,
                                  {'sale_order_line_id': sale.order_line[1].id,
                                   'quantity': 2}),
                                 (0, 0,
                                  {'sale_order_line_id': sale.order_line[2].id,
                                   'quantity': 8}),
                                 ],
                    }
        ids = self.inv_par_model.create(cr, uid, wiz_data,
                                        context=context)
        second_invoice_id = self.inv_par_model.\
            create_invoice(cr, uid, [ids], context=context)['res_id']
        invoice = self.account_invoice_model.browse(cr, uid, second_invoice_id)
        self.assertEqual(len(invoice.invoice_line), 3,
                         "Wrong number of lines in second invoice")

        """ Check the 2nd invoice is created """
        order = self.sale_order_model.browse(cr, uid, sale.id)
        self.assertEqual(len(order.invoice_ids), 2,
                         "I should have 2 invoices")

        """ Check qty_invoiced """
        self.assertEqual(order.order_line[0].qty_invoiced, 3,
                         "qty_invoiced not correctly implemented")
        self.assertEqual(order.order_line[1].qty_invoiced, 3,
                         "qty_invoiced not correctly implemented")
        self.assertEqual(order.order_line[2].qty_invoiced, 12,
                         "qty_invoiced not correctly implemented")

        """  Check qty_delivered """
        self.assertEqual(order.order_line[0].qty_delivered, 3,
                         "qty_delivered not correctly implemented")
        self.assertEqual(order.order_line[1].qty_delivered, 3,
                         "qty_delivered not correctly implemented")
        self.assertEqual(order.order_line[2].qty_delivered, 12,
                         "qty_delivered not correctly implemented")

        """ Check SO state """
        sale = self.sale_order_model.browse(cr, uid, sale.id)
        self.assertEqual(sale.state, 'manual')

        """ Confirm the invoices """
        sale = self.sale_order_model.browse(cr, uid, sale.id)
        wf_service = netsvc.LocalService("workflow")
        so = self.sale_order_model.browse(cr, uid, sale.id)
        for invoice in so.invoice_ids:
            wf_service.trg_validate(uid, 'account.invoice', invoice.id,
                                    'invoice_open', cr)
        order = self.sale_order_model.browse(cr, uid, sale.id)
        journal_ids = self.account_journal_model.\
            search(cr, uid, [('type', '=', 'cash'),
                             ('company_id', '=', order.company_id.id)],
                   limit=1)
        for invoice in order.invoice_ids:
            invoice.pay_and_reconcile(invoice.amount_total,
                                      self.account_cash_id,
                                      self.account_period_8_id,
                                      journal_ids[0],
                                      self.account_cash_id,
                                      self.account_period_8_id,
                                      journal_ids[0],
                                      name='test')

        """Run the scheduler(required to get the correct sale order state)"""
        self.procurement_order_model.run_scheduler(cr, uid)

        """ check sale order """
        order = self.sale_order_model.browse(cr, uid, sale.id)
        self.assertTrue(order.invoice_ids, "Invoice should be created.")
        self.assertTrue(order.invoice_exists, "Order is not invoiced.")
        self.assertTrue(order.invoiced, "Order is not paid.")
        self.assertEqual(order.state, 'done', 'Order should be Done.')
