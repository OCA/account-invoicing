# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
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

from openerp import models, api, _
from openerp.exceptions import Warning


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_partner_to_invoice(self, picking):
        partner_obj = self.env['res.partner']
        partner = super(StockPicking, self)._get_partner_to_invoice(picking)
        if isinstance(partner, int):
            partner = partner_obj.browse(partner)
        if picking.partner_id.id != partner.id:
            # if someone else modified invoice partner, I use it
            return partner.id
        return partner.address_get(
            ['invoice'])['invoice']

    @api.multi
    def set_to_be_invoiced(self):
        for picking in self:
            if picking.invoice_state == '2binvoiced':
                raise Warning(_("Can't update invoice control for picking %s: "
                                "It's 'to be invoiced' yet") % picking.name)
            if picking.invoice_state in ('none', 'invoiced'):
                if picking.invoice_id:
                    raise Warning(_('Picking %s has linked invoice %s') %
                                  (picking.name, picking.invoice_id.number))
                picking.invoice_state = '2binvoiced'
        return True
