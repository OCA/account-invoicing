# Copyright 2004-2010 Tiny SPRL (http://tiny.be).
# Copyright 2010-2011 Elico Corp.
# Copyright 2016 Acsone (https://www.acsone.eu/)
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, exceptions, fields, models
from odoo.tools.translate import _


class InvoiceMerge(models.TransientModel):
    _name = "invoice.merge"
    _description = "Merge Partner Invoice"

    keep_references = fields.Boolean('Keep references from original invoices',
                                     default=True)
    date_invoice = fields.Date('Invoice Date')

    @api.model
    def _dirty_check(self):
        if self.env.context.get('active_model', '') == 'account.invoice':
            ids = self.env.context['active_ids']
            if len(ids) < 2:
                raise exceptions.Warning(
                    _('Please select multiple invoices to merge in the list '
                      'view.'))

            invs = self.env['account.invoice'].browse(ids)
            for d in invs:
                if d['state'] != 'draft':
                    raise exceptions.Warning(
                        _('At least one of the selected invoices is %s!') %
                        d['state'])
                if d['account_id'] != invs[0]['account_id']:
                    raise exceptions.Warning(
                        _('Not all invoices use the same account!'))
                if d['company_id'] != invs[0]['company_id']:
                    raise exceptions.Warning(
                        _('Not all invoices belong to the same company!'))
                if d['partner_id'] != invs[0]['partner_id']:
                    raise exceptions.Warning(
                        _('Not all invoices are from the same partner!'))
                if d['type'] != invs[0]['type']:
                    raise exceptions.Warning(
                        _('Not all invoices are from the same type!'))
                if d['currency_id'] != invs[0]['currency_id']:
                    raise exceptions.Warning(
                        _('The currency in the invoices is different!'))
                if d['journal_id'] != invs[0]['journal_id']:
                    raise exceptions.Warning(
                        _('All invoices must belong to the same journal!'))
        return {}

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Changes the view dynamically
         @param self: The object pointer.
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
            'out_refund': 'action_invoice_tree3',
            'in_invoice': 'action_invoice_tree2',
            'in_refund': 'action_invoice_tree4',
        }[invoices[0].type]
        action = aw_obj.for_xml_id('account', xid)
        # allinvoices.keys()
        action.update({
            'domain': [('id', 'in', ids + list(allinvoices))],
        })
        return action
