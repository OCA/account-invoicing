# -*- coding: utf-8 -*-
##############################################################################
#
#    account_invoice_total module for OpenERP
#    Copyright (C) 2012 Ren Dao Solutions (<http://rendaosolutions.com>).
#    Copyright (C) 2012 Acsone (<http://acsone.eu>).
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

from osv import fields, osv
from tools.translate import _

class account_invoice_total(osv.osv):
    _inherit = 'account.invoice'
  
    def action_move_create(self, cr, uid, ids, context=None):
        res = super(account_invoice_total, self).action_move_create(cr, uid, ids, context=context)
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0):
                raise osv.except_osv(_('Bad total !'), _('Please verify the price of the invoice !\nThe real total does not match the computed total.'))
        return res

account_invoice_total()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
