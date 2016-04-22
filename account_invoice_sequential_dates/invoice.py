# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2010 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp import _

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def action_number(self, cr, uid, ids, context=None):
        super(account_invoice, self).action_number(cr, uid, ids, context=context)
        for obj_inv in self.browse(cr, uid, ids, context=context):
            inv_type = obj_inv.type
            if inv_type == 'in_invoice' or inv_type == 'in_refund':
                return True
            number = obj_inv.number
            date_invoice = obj_inv.date_invoice
            journal = obj_inv.journal_id.id
            res = self.search(cr, uid, [('type','=',inv_type),('date_invoice','>',date_invoice), 
                ('number', '<', number), ('journal_id','=',journal)], context=context)
            if res:
                raise orm.except_orm(_('Date Inconsistency'),
                        _('Cannot create invoice! Post the invoice with a greater date'))
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
