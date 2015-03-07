# -*- coding: utf-8 -*-
##############################################################################

#     This file is part of account_invoice_shipping_address, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_line_sort is free software: you can redistribute it
#     and/or modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     account_invoice_line_sort is distributed in the hope that it will
#     be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with account_invoice_line_sort.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tests.common as common


class TestAccountInvoiceShippement(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceShippement, self).setUp()
        self.inv_model = self.env['account.invoice']
        self.stock_model = self.env['stock.picking']

        self.partner_2 = self.ref('base.res_partner_2')
        self.partner_address_3 = self.ref('base.res_partner_address_3')
        self.shipment4 = self.ref('stock.incomming_shipment4')
        self.account_journal = self.ref('account.check_journal') 

    def test_create_invoice_from_stock(self):
        stock = self.stock_model.browse(self.shipment4)

        stock.invoice_state = '2binvoiced'
        stock.partner_id = self.partner_address_3
        stock.move_lines[0].partner_id = self.partner_2

        res = stock.action_invoice_create(journal_id=self.account_journal)
        self.assertEqual(len(res), 1)
        inv_id = res[0]

        created_invoice = self.inv_model.browse(inv_id)

        self.assertEqual(created_invoice.partner_id.id, self.partner_address_3)
        self.assertEqual(created_invoice.address_shipping_id.id, self.partner_2)
