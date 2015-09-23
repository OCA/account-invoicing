# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp import models, api
from openerp import workflow
from openerp.osv.orm import browse_record, browse_null


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _get_invoice_key_cols(self):
        return [
            'partner_id', 'user_id', 'type', 'account_id', 'currency_id',
            'journal_id', 'company_id', 'partner_bank_id',
        ]

    @api.model
    def _get_invoice_line_key_cols(self):
        fields = [
            'name', 'origin', 'discount', 'invoice_line_tax_id', 'price_unit',
            'product_id', 'account_id', 'account_analytic_id',
        ]
        for field in ['analytics_id']:
            if field in self.env['account.invoice.line']._fields:
                fields.append(field)
        return fields

    @api.model
    def _get_first_invoice_fields(self, invoice):
        return {
            'origin': '%s' % (invoice.origin or '',),
            'partner_id': invoice.partner_id.id,
            'journal_id': invoice.journal_id.id,
            'user_id': invoice.user_id.id,
            'currency_id': invoice.currency_id.id,
            'company_id': invoice.company_id.id,
            'type': invoice.type,
            'account_id': invoice.account_id.id,
            'state': 'draft',
            'reference': '%s' % (invoice.reference or '',),
            'name': '%s' % (invoice.name or '',),
            'fiscal_position': invoice.fiscal_position.id,
            'payment_term': invoice.payment_term.id,
            'period_id': invoice.period_id.id,
            'invoice_line': {},
            'partner_bank_id': invoice.partner_bank_id.id,
        }

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        """
        To merge similar type of account invoices.
        Invoices will only be merged if:
        * Account invoices are in draft
        * Account invoices belong to the same partner
        * Account invoices are have same company, partner, address, currency,
          journal, currency, salesman, account, type
        Lines will only be merged if:
        * Invoice lines are exactly the same except for the quantity and unit

         @param self: The object pointer.
         @param keep_references: If True, keep reference of original invoices

         @return: new account invoice id

        """
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'account_id'):
                    if not field_val:
                        field_val = False
                if (isinstance(field_val, browse_record) and
                   field != 'invoice_line_tax_id'):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif (isinstance(field_val, list) or
                      field == 'invoice_line_tax_id'):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

        # compute what the new invoices should contain

        new_invoices = {}
        draft_invoices = [invoice
                          for invoice in self
                          if invoice.state == 'draft']
        seen_origins = {}
        seen_client_refs = {}

        for account_invoice in draft_invoices:
            invoice_key = make_key(
                account_invoice, self._get_invoice_key_cols())
            new_invoice = new_invoices.setdefault(invoice_key, ({}, []))
            origins = seen_origins.setdefault(invoice_key, set())
            client_refs = seen_client_refs.setdefault(invoice_key, set())
            new_invoice[1].append(account_invoice.id)
            invoice_infos = new_invoice[0]
            if not invoice_infos:
                invoice_infos.update(
                    self._get_first_invoice_fields(account_invoice))
                origins.add(account_invoice.origin)
                client_refs.add(account_invoice.reference)
                if not keep_references:
                    invoice_infos.pop('name')
            else:
                if account_invoice.name and keep_references:
                    invoice_infos['name'] = \
                        (invoice_infos['name'] or '') + \
                        (' %s' % (account_invoice.name,))
                if account_invoice.origin and \
                        account_invoice.origin not in origins:
                    invoice_infos['origin'] = \
                        (invoice_infos['origin'] or '') + ' ' + \
                        account_invoice.origin
                    origins.add(account_invoice.origin)
                if account_invoice.reference \
                        and account_invoice.reference not in client_refs:
                    invoice_infos['reference'] = \
                        (invoice_infos['reference'] or '') + \
                        (' %s' % (account_invoice.reference,))
                    client_refs.add(account_invoice.reference)
            for invoice_line in account_invoice.invoice_line:
                line_key = make_key(
                    invoice_line, self._get_invoice_line_key_cols())
                o_line = invoice_infos['invoice_line'].setdefault(line_key, {})
                uos_factor = (invoice_line.uos_id and
                              invoice_line.uos_id.factor or 1.0)
                if o_line:
                    # merge the line with an existing line
                    o_line['quantity'] += invoice_line.quantity * \
                        uos_factor / o_line['uom_factor']
                else:
                    # append a new "standalone" line
                    for field in ('quantity', 'uos_id'):
                        field_val = getattr(invoice_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line['uom_factor'] = uos_factor
        allinvoices = []
        invoices_info = {}
        for invoice_key, (invoice_data, old_ids) in new_invoices.iteritems():
            # skip merges with only one invoice
            if len(old_ids) < 2:
                allinvoices += (old_ids or [])
                continue
            # cleanup invoice line data
            for key, value in invoice_data['invoice_line'].iteritems():
                del value['uom_factor']
                value.update(dict(key))
            invoice_data['invoice_line'] = [
                (0, 0, value) for value in
                invoice_data['invoice_line'].itervalues()]
            if date_invoice:
                invoice_data['date_invoice'] = date_invoice
            # create the new invoice
            newinvoice = self.with_context(is_merge=True).create(invoice_data)
            invoices_info.update({newinvoice.id: old_ids})
            allinvoices.append(newinvoice.id)
            # make triggers pointing to the old invoices point to the new
            # invoice
            for old_id in old_ids:
                workflow.trg_redirect(
                    self.env.uid, 'account.invoice', old_id, newinvoice.id,
                    self.env.cr)
                workflow.trg_validate(
                    self.env.uid, 'account.invoice', old_id, 'invoice_cancel',
                    self.env.cr)
        # make link between original sale order or purchase order
        # None if sale is not installed
        so_obj = self.env['sale.order']\
            if 'sale.order' in self.env.registry else False
        invoice_line_obj = self.env['account.invoice.line']
        for new_invoice_id in invoices_info:
            if so_obj is not False:
                todos = so_obj.search(
                    [('invoice_ids', 'in', invoices_info[new_invoice_id])])
                todos.write({'invoice_ids': [(4, new_invoice_id)]})
                for org_so in todos:
                    for so_line in org_so.order_line:
                        invoice_line_ids = invoice_line_obj.search(
                            [('product_id', '=', so_line.product_id.id),
                             ('invoice_id', '=', new_invoice_id)])
                        if invoice_line_ids:
                            invoice_line_ids_list = [x.id for x in invoice_line_ids]
                            so_line.write(
                                {'invoice_lines': [(6, 0, invoice_line_ids_list)]})
        # recreate link (if any) between original analytic account line
        # (invoice time sheet for example) and this new invoice
        anal_line_obj = self.env['account.analytic.line']
        if 'invoice_id' in anal_line_obj._columns:
            for new_invoice_id in invoices_info:
                todos = anal_line_obj.search(
                    [('invoice_id', 'in', invoices_info[new_invoice_id])])
                todos.write({'invoice_id': new_invoice_id})
        return invoices_info
