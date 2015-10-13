# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from osv import fields, osv
from tools.translate import _

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'corrispettivo': fields.boolean('Corrispettivo'),
        }

    def onchange_company_id(self, cr, uid, ids, company_id, part_id, type, invoice_line, currency_id, context=None):
        if not context:
            context={}
        journal_obj = self.pool.get('account.journal')
        res = super(account_invoice, self).onchange_company_id(cr, uid, ids, company_id, part_id, type, invoice_line, currency_id)
        is_corrispettivo = context.get('corrispettivo', False)
        corr_journal_ids = journal_obj.search(cr, uid, [('corrispettivi','=', True), ('company_id','=', company_id)])

        # Se è un corrispettivo e la company ha almeno un sezionale corrispettivi
        if is_corrispettivo and corr_journal_ids:
            res['value']['journal_id']  = corr_journal_ids[0]

        # Se la company ha almeno un sezionale corrispettivi ma l'invoice non è un corrispettivo
        elif corr_journal_ids and corr_journal_ids[0] in res['domain']['journal_id'][0][2]:
            # Se l'on_change di invoice ha impostato il journal corrispettivi
            if corr_journal_ids[0] == res['value']['journal_id'] and len(res['domain']['journal_id'][0][2]) > 1:
                for j_id in res['domain']['journal_id'][0][2]:
                    if corr_journal_ids[0] != j_id:
                        res['value']['journal_id'] = j_id
                        break
        return res


    def _get_account(self, cr, uid, context=None):
        if context is None:
            context = {}
        is_corrispettivo = context.get('corrispettivo', False)
        res = False
        if is_corrispettivo:
            partner_obj = partner_ids = self.pool.get('res.partner')
            partner_ids=partner_obj.search(cr, uid, [('corrispettivi', '=', True)])
            if not partner_ids:
                raise osv.except_osv(_('Error!'), 
                     _('No partner "corrispettivi" found'))
            partner = partner_obj.browse(cr, uid, partner_ids[0])
            res = partner.property_account_receivable.id
        return res

    def _get_partner_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        is_corrispettivo = context.get('corrispettivo', False)
        res = False
        if is_corrispettivo:
            partner_obj = partner_ids = self.pool.get('res.partner')
            partner_ids=partner_obj.search(cr, uid, [('corrispettivi', '=', True)])
            if not partner_ids:
                raise osv.except_osv(_('Error!'), 
                     _('No partner "corrispettivi" found'))
            res = partner_ids[0]
        return res

    def onchange_corrispettivo(self, cr, uid, ids, corrispettivo=False, context=None):
        res = {}
        user_obj = self.pool.get('res.users')
        journal_obj = self.pool.get('account.journal') 
        company_id = user_obj.browse(cr,uid,uid).company_id.id
        corr_journal_ids = journal_obj.search(cr, uid, [('corrispettivi','=', True), ('company_id','=', company_id)])
        if corr_journal_ids and corrispettivo:
            res = {'value': {'journal_id': corr_journal_ids[0]}}
        return res

    _defaults = {
        'partner_id': _get_partner_id,
        'account_id': _get_account,
        }

account_invoice()

class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
        'corrispettivi': fields.boolean('Corrispettivi'),
        }
account_journal()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'corrispettivi': fields.boolean('Corrispettivi'),
        }
res_partner()
