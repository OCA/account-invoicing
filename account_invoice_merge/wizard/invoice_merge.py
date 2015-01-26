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
from openerp import models, api, exceptions
from openerp.tools.translate import _


class invoice_merge(models.TransientModel):
    _name = "invoice.merge"
    _description = "Merge Partner Invoice"

    @api.model
    def _dirty_check(self):
        if self.env.context.get('active_model', '') == 'account.invoice':
            ids = self.env.context['active_ids']
            if len(ids) < 2:
                raise exceptions.except_orm(
                    _('Warning!'),
                    _('Please select multiple invoice to merge in the list '
                      'view.'))
            inv_obj = self.env['account.invoice']
            invs = inv_obj.read(ids,
                                ['account_id', 'state', 'type', 'company_id',
                                 'partner_id', 'currency_id', 'journal_id'])
            for d in invs:
                if d['state'] != 'draft':
                    raise exceptions.except_orm(
                        _('Warning'),
                        _('At least one of the selected invoices is %s!') %
                        d['state'])
                if d['account_id'] != invs[0]['account_id']:
                    raise exceptions.except_orm(
                        _('Warning'),
                        _('Not all invoices use the same account!'))
                if d['company_id'] != invs[0]['company_id']:
                    raise exceptions.except_orm(
                        _('Warning'),
                        _('Not all invoices are at the same company!'))
                if d['partner_id'] != invs[0]['partner_id']:
                    raise exceptions.except_orm(
                        _('Warning'),
                        _('Not all invoices are for the same partner!'))
                if d['type'] != invs[0]['type']:
                    raise exceptions.except_orm(
                        _('Warning'),
                        _('Not all invoices are of the same type!'))
                if d['currency_id'] != invs[0]['currency_id']:
                    raise exceptions.except_orm(
                        _('Warning'),
                        _('Not all invoices are at the same currency!'))
                if d['journal_id'] != invs[0]['journal_id']:
                    raise exceptions.except_orm(
                        _('Warning'),
                        _('Not all invoices are at the same journal!'))
        return {}

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Changes the view dynamically
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view.
        """
        res = super(invoice_merge, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=False)
        self._dirty_check()
        return res

    @api.multi
    def merge_invoices(self):
        """To merge similar type of account invoices.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: account invoice view
        """
        inv_obj = self.env['account.invoice']
        mod_obj = self.env['ir.model.data']
        result = mod_obj._get_id('account', 'invoice_form')
        data = mod_obj.search_read([('id', '=', result)], ['res_id'])[0]\
            or False
        invoices = inv_obj.browse(self.env.context.get('active_ids', []))
        allinvoices = invoices.do_merge()
        return {
            'domain': [('id', 'in', allinvoices.keys())],
            'name': _('Partner Invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'search_view_id': data['res_id']
        }
