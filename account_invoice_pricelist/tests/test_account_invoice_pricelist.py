# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV <http://therp.nl>.
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
from openerp.tests.common import TransactionCase


class TestAccountInvoicePricelist(TransactionCase):
    def test_account_invoice_pricelist(self):
        invoice = self.env['account.invoice'].search([
            ('type', '=', 'out_invoice'),
            ('partner_id.property_product_pricelist', '!=', False)
        ], limit=1)
        on_change_partner_id = invoice.onchange_partner_id(
            invoice.type, invoice.partner_id.id)
        self.assertEqual(
            on_change_partner_id['value']['pricelist_id'],
            invoice.partner_id.property_product_pricelist.id)
        invoice.button_update_prices_from_pricelist()
