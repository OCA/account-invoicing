# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Invoice partner test module for OpenERP
#    Copyright (C) 2015 ACSONE SA/NV (http://acsone.eu)
#    @author Laurent Mignon <laurent.mignon@acsone.eu>
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

import openerp.tests.common as common


class TestAccountInvoiceParner(common.TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceParner, self).setUp()
        self.inv_model = self.env['account.invoice']
        self.partner_model = self.env['res.partner']
        self.partner_2 = self.ref('base.res_partner_2')
        self.partner_address_3 = self.ref('base.res_partner_address_3')

    def test_0(self):
        # partner_2 has no address defined for invoice
        addr_ids = self.partner_model.search(
            [('parent_id', '=', self.partner_2),
             ('type', '=', 'invoice')])
        self.assertFalse(addr_ids)
        res = self.inv_model.onchange_partner_id(
            invoice_type='in_invoice', partner_id=self.partner_2)
        self.assertFalse('partner_id' in res['value'])

        # declare partner_address3 as invoice address
        self.partner_model.browse(self.partner_address_3).write(
            {'type': 'invoice'})
        res = self.inv_model.onchange_partner_id(
            invoice_type='in_invoice', partner_id=self.partner_2)
        self.assertEqual(self.partner_address_3, res['value']['partner_id'])
