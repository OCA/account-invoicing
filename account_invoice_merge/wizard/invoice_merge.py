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
from openerp import models, fields, api, exceptions
from openerp.tools.translate import _


class invoice_merge(models.TransientModel):
    _name = "invoice.merge"
    _description = "Merge Partner Invoice"

    keep_references = fields.Boolean('Keep references'
                                     ' from original invoices',
                                     default=True)
    date_invoice = fields.Date('Invoice Date')

    @api.model
    def _dirty_check(self):
        print self.env.context
        if self.env.context.get('active_model', '') == 'account.invoice':
            ids = self.env.context['active_ids']
            if len(ids) < 2:
                raise exceptions.Warning(
                    _('Please select multiple invoice to merge in the list '
                      'view.'))
            inv_obj = self.env['account.invoice']
            invs = inv_obj.browse(ids)
            for d in invs:
                if d.state != 'draft':
                    raise exceptions.Warning(
                        _('At least one of the selected invoices is %s!') %
                        d['state'])
                if d.account_id.id != invs[0].account_id.id:
                    raise exceptions.Warning(
                        _('Not all invoices use the same account!'))
                if d.company_id.id != invs[0].company_id.id:
                    raise exceptions.Warning(
                        _('Not all invoices are at the same company!'))
                if d.partner_id.id != invs[0].partner_id.id:
                    raise exceptions.Warning(
                        _('Not all invoices are for the same partner!'))
                if d.type != invs[0].type:
                    raise exceptions.Warning(
                        _('Not all invoices are of the same type!'))
                if d.currency_id.id != invs[0].currency_id.id:
                    raise exceptions.Warning(
                        _('Not all invoices are at the same currency!'))
                if d.journal_id.id != invs[0].journal_id.id:
                    raise exceptions.Warning(
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

             @return: account invoice action
        """
        inv_obj = self.env['account.invoice']
        aw_obj = self.env['ir.actions.act_window']
        ids = self.env.context.get('active_ids', [])
        invoices = inv_obj.browse(ids)
        allinvoices = invoices.do_merge(keep_references=self.keep_references,
                                        date_invoice=self.date_invoice)
        xid = {
            'out_invoice': 'action_invoice_tree1',
            'out_refund': 'action_invoice_tree1',
            'in_invoice': 'action_invoice_tree2',
            'in_refund': 'action_invoice_tree2',
        }[invoices[0].type]
        action = aw_obj.for_xml_id('account', xid)
        action.update({
            'domain': [('id', 'in', ids)],
        })
        return action
