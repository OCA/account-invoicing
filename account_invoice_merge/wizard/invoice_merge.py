# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
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

from openerp.osv import orm
from openerp.tools.translate import _


class invoice_merge(orm.TransientModel):
    _name = "invoice.merge"
    _description = "Merge Partner Invoice"

    def _dirty_check(self, cr, uid, context):
        if context.get('active_model', '') == 'account.invoice':
            ids = context['active_ids']
            if len(ids) < 2:
                raise orm.except_orm(
                    _('Warning!'),
                    _('Please select multiple invoice to merge in the list '
                      'view.'))
            inv_obj = self.pool.get('account.invoice')
            invs = inv_obj.read(cr, uid, ids,
                                ['account_id', 'state', 'type', 'company_id',
                                 'partner_id', 'currency_id', 'journal_id'])
            for d in invs:
                if d['state'] != 'draft':
                    raise orm.except_orm(
                        _('Warning'),
                        _('At least one of the selected invoices is %s!') %
                        d['state'])
                if d['account_id'] != invs[0]['account_id']:
                    raise orm.except_orm(
                        _('Warning'),
                        _('Not all invoices use the same account!'))
                if d['company_id'] != invs[0]['company_id']:
                    raise orm.except_orm(
                        _('Warning'),
                        _('Not all invoices are at the same company!'))
                if d['partner_id'] != invs[0]['partner_id']:
                    raise orm.except_orm(
                        _('Warning'),
                        _('Not all invoices are for the same partner!'))
                if d['type'] != invs[0]['type']:
                    raise orm.except_orm(
                        _('Warning'),
                        _('Not all invoices are of the same type!'))
                if d['currency_id'] != invs[0]['currency_id']:
                    raise orm.except_orm(
                        _('Warning'),
                        _('Not all invoices are at the same currency!'))
                if d['journal_id'] != invs[0]['journal_id']:
                    raise orm.except_orm(
                        _('Warning'),
                        _('Not all invoices are at the same journal!'))
        return {}

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """Changes the view dynamically
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view.
        """
        if context is None:
            context = {}
        res = super(invoice_merge, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=False)
        self._dirty_check(cr, uid, context)
        return res

    def merge_invoices(self, cr, uid, ids, context=None):
        """To merge similar type of account invoices.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: account invoice view
        """
        inv_obj = self.pool['account.invoice']
        mod_obj = self.pool['ir.model.data']
        if context is None:
            context = {}
        result = mod_obj._get_id(cr, uid, 'account', 'invoice_form')
        record = mod_obj.read(cr, uid, result, ['res_id'])
        allinvoices = inv_obj.do_merge(
            cr, uid, context.get('active_ids', []), context)
        return {
            'domain': "[('id','in',[" +
                      ','.join(map(str, allinvoices.keys())) + "])]",
            'name': _('Partner Invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'search_view_id': record['res_id']
        }
