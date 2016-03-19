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

import logging
from openerp import models, api, fields, _
from openerp.exceptions import Warning

_logger = logging.getLogger(__name__)

INVOICE_STATE = [
            ("invoiced", "Invoiced"),
            ("2binvoiced", "To Be Invoiced"),
            ("none", "Not Applicable")
            ]



class StockLocationPath(models.Model):
    _inherit = "stock.location.path"
    
    invoice_state =  fields.Selection(INVOICE_STATE, 
                                        string="Invoice Status", default="none")
    
    
    @api.v7
    def _prepare_push_apply(self, cr, uid, rule, move, context=None):
        res = super(stock_location_path, self)._prepare_push_apply(cr, uid, rule, move, context=context)
        res['invoice_state'] = rule.invoice_state or 'none'
        return res

#----------------------------------------------------------
# Procurement Rule
#----------------------------------------------------------
class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'
    
    invoice_state =  fields.Selection(INVOICE_STATE, 
                                        string="Invoice Status", default="none")

#----------------------------------------------------------
# Procurement Order
#----------------------------------------------------------


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"
    
    
    invoice_state =  fields.Selection(INVOICE_STATE, 
                                        string="Invoice Status", default="none")

    @api.v7
    def _run_move_create(self, cr, uid, procurement, context=None):
        res = super(procurement_order, self)._run_move_create(cr, uid, procurement, context=context)
        res.update({'invoice_state': procurement.rule_id.invoice_state or procurement.invoice_state or 'none'})
        return res



#----------------------------------------------------------
# Move
#----------------------------------------------------------

class stock_move(models.Model):
    _inherit = "stock.move"

    invoice_state =  fields.Selection(INVOICE_STATE, 
                                        string="Invoice Status", default="none")

    @api.model
    def _get_master_data(self, move, company):
        data = super(StockMove, self)._get_master_data(move, company)
        if move.picking_id.partner_id.id != data[0].id:
            # if someone else modified invoice partner, I use it
            return data
        partner_invoice_id = move.picking_id.partner_id.address_get(
            ['invoice'])['invoice']
        partner = self.env['res.partner'].browse(partner_invoice_id)
        new_data = partner, data[1], data[2]
        return new_data



#----------------------------------------------------------
# Picking
#----------------------------------------------------------

class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_state =  fields.Selection(INVOICE_STATE, 
                                        string="Invoice Status", default="none")
    
    
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

