# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import openerp.tests.common as test_common


class TestPickingInvoicing(test_common.SingleTransactionCase):

    def setUp(self):
        super(TestPickingInvoicing, self).setUp()
        self.picking_model = self.env['stock.picking']
        self.move_model = self.env['stock.move']
        self.invoice_wizard = self.env['stock.invoice.onshipping']
        self.invoice_model = self.env['account.invoice']
        self.partner_model = self.env['res.partner']

    def test_0_picking_invoicing(self):
        agrolait = self.partner_model.browse(self.ref('base.res_partner_2'))
        # setting Agrolait type to default, because it's 'contact' in demo data
        agrolait.write({'type': 'default'})
        picking = self.picking_model.create({
            # using Agrolait, Michel Fletcher
            'partner_id': self.ref('base.res_partner_address_4'),
            'picking_type_id': self.ref('stock.picking_type_in'),
            })
        prod_id = self.ref('product.product_product_10')
        move_vals = self.move_model.onchange_product_id(
            prod_id=prod_id)['value']
        move_vals['product_id'] = prod_id
        move_vals['picking_id'] = picking.id
        move_vals['location_dest_id'] = self.ref(
            'stock.stock_location_customers')
        move_vals['location_id'] = self.ref(
            'stock.stock_location_stock')
        self.move_model.create(move_vals)
        picking.set_to_be_invoiced()
        picking.action_confirm()
        picking.action_assign()
        picking.do_prepare_partial()
        picking.do_transfer()
        self.assertEqual(picking.state, 'done')
        wizard = self.invoice_wizard.with_context(
            {
                'active_ids': [picking.id],
                'active_model': 'stock.picking',
                'active_id': picking.id,
            }
        ).create({'journal_id': self.ref('account.sales_journal')})
        invoices = wizard.create_invoice()
        self.assertEqual(picking.invoice_state, 'invoiced')
        invoice = self.invoice_model.browse(invoices[0])
        # invoice partner must be Agrolait
        self.assertEqual(invoice.partner_id.id, self.ref('base.res_partner_2'))
