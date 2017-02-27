# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
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

from openerp import models, fields, api


class account_invoice(models.Model):
    _inherit = "account.invoice"

    address_shipping_id = fields.Many2one(
        'res.partner',
        'Shipping Address',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
        help="Delivery address for current invoice.")

    @api.onchange('partner_id')
    def onchange_partner(self):
	self.ensure_one()
	if self.address_shipping_id:
		return

	delivery = None
	for contact in self.partner_id.child_ids:
		if contact.type == 'delivery':
			delivery = contact

	if not delivery:
		return

	self.address_shipping_id = delivery
