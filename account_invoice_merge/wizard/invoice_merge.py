# -*- coding: utf-8 -*-
# © 2010-2011 Ian Li <ian.li@elico-corp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class InvoiceMerge(models.TransientModel):
    _name = "invoice.merge"
    _description = "Merge Partner Invoice"

    keep_references = fields.Boolean(
        string='Keep references from original invoices', default=True)
    date_invoice = fields.Date('Invoice Date')

    @api.model
    def _dirty_check(self):
        if self._context.get('active_model') == 'account.invoice':
            ids = self._context['active_ids']
            if len(ids) < 2:
                raise UserError(
                    _('Please select multiple invoice to merge in the list '
                      'view.'))
            invs = self.env['account.invoice'].browse(ids)
            for i, inv in enumerate(invs):
                if inv.state != 'draft':
                    raise UserError(
                        _('At least one of the selected invoices is %s!') %
                        inv.state)
                if i > 0:
                    if inv.account_id != invs[0].account_id:
                        raise UserError(
                            _('Not all invoices use the same account!'))
                    if inv.company_id != invs[0].company_id:
                        raise UserError(
                            _('Not all invoices are at the same company!'))
                    if inv.partner_id != invs[0].partner_id:
                        raise UserError(
                            _('Not all invoices are for the same partner!'))
                    if inv.type != invs[0].type:
                        raise UserError(
                            _('Not all invoices are of the same type!'))
                    if inv.currency_id != invs[0].currency_id:
                        raise UserError(
                            _('Not all invoices are at the same currency!'))
                    if inv.journal_id != invs[0].journal_id:
                        raise UserError(
                            _('Not all invoices are at the same journal!'))
                    if inv.partner_bank_id != invs[0].partner_bank_id:
                        raise UserError(
                            _('Not all invoices have the same '
                              'Partner Bank Account!'))

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
        res = super(InvoiceMerge, self).fields_view_get(
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
        aw_obj = self.env['ir.actions.act_window']
        ids = self._context.get('active_ids', [])
        invoices = self.env['account.invoice'].browse(ids)
        allinvoices = invoices.do_merge(keep_references=self.keep_references,
                                        date_invoice=self.date_invoice)[0]
        xid = {
            'out_invoice': 'action_invoice_tree1',
            'out_refund': 'action_invoice_tree3',
            'in_invoice': 'action_invoice_tree2',
            'in_refund': 'action_invoice_tree4',
        }[invoices[0].type]
        action = aw_obj.for_xml_id('account', xid)
        action.update({
            'domain': [('id', 'in', list(ids) + allinvoices.keys())],
        })
        return action
