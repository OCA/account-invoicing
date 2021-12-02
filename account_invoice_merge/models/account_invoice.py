# -*- coding: utf-8 -*-
# Copyright 2004-2010 Tiny SPRL (http://tiny.be).
# Copyright 2010-2011 Elico Corp.
# Copyright 2016 Acsone (https://www.acsone.eu/)
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json
from odoo import api, models
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
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
            'name', 'origin', 'discount', 'invoice_line_tax_ids', 'price_unit',
            'product_id', 'account_id', 'account_analytic_id',
            'uom_id'
        ]
        if 'sale_line_ids' in self.env['account.invoice.line']._fields:
            fields.append('sale_line_ids')
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
            'fiscal_position_id': invoice.fiscal_position_id.id,
            'payment_term_id': invoice.payment_term_id.id,
            'invoice_line_ids': {},
            'partner_bank_id': invoice.partner_bank_id.id,
        }

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False,
                 remove_empty_invoice_lines=True):
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

        def make_field_dict(record, fields):
            values = {}
            for field in fields:
                value = getattr(record, field)
                values[field] = value
            return record._convert_to_write(values)

        # compute what the new invoices should contain
        new_invoices = {}
        origins = []
        client_refs = []
        for invoice in self:
            if invoice.state != 'draft':
                continue
            same_infos = make_field_dict(
                invoice, self._get_invoice_key_cols())
            invoice_key = json.dumps(same_infos)
            invoice_infos = new_invoices.setdefault(
                invoice_key,
                self._get_first_invoice_fields(invoice))
            invoice_infos.update(same_infos)
            if 'ids' not in invoice_infos:
                invoice_infos['ids'] = []
            invoice_infos['ids'].append(invoice.id)
            if invoice.name and keep_references:
                invoice_infos['name'] = \
                    (invoice_infos['name'] or '') + ' ' + \
                    invoice.name
            if invoice.origin and \
                    invoice.origin not in origins:
                invoice_infos['origin'] = \
                    (invoice_infos['origin'] or '') + ' ' + \
                    invoice.origin
                origins.append(invoice.origin)
            if invoice.reference \
                    and invoice.reference not in client_refs:
                invoice_infos['reference'] = \
                    (invoice_infos['reference'] or '') + ' ' + \
                    invoice.reference
                client_refs.append(invoice.reference)

            for invoice_line in invoice.invoice_line_ids:
                line_infos = make_field_dict(
                    invoice_line, self._get_invoice_line_key_cols())
                line_key = json.dumps(line_infos)
                o_line = invoice_infos['invoice_line_ids'].get(line_key)
                if o_line:
                    # merge the line with an existing line
                    o_line['quantity'] += invoice_line.quantity
                else:
                    # append a new "standalone" line
                    invoice_infos['invoice_line_ids'][line_key] = line_infos
                    invoice_infos['invoice_line_ids'][line_key]['quantity'] = \
                        invoice_line.quantity

        allinvoices = []
        allnewinvoices = []
        invoices_info = {}
        qty_prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for invoice_key, invoice_data in new_invoices.iteritems():
            # skip merges with only one invoice
            old_ids = invoice_data['ids']
            if len(old_ids) < 2:
                allinvoices += (old_ids or [])
                continue

            if remove_empty_invoice_lines:
                invoice_data['invoice_line_ids'] = [
                    (0, 0, value) for value in
                    invoice_data['invoice_line_ids'].itervalues() if
                    not float_is_zero(
                        value['quantity'], precision_digits=qty_prec)]
            else:
                invoice_data['invoice_line_ids'] = [
                    (0, 0, value) for value in
                    invoice_data['invoice_line_ids'].itervalues()]

            if date_invoice:
                invoice_data['date_invoice'] = date_invoice

            # create the new invoice
            newinvoice = self.with_context(is_merge=True).create(invoice_data)
            invoices_info.update({newinvoice.id: old_ids})
            allinvoices.append(newinvoice.id)
            allnewinvoices.append(newinvoice)
            # cancel old invoices
            old_invoices = self.env['account.invoice'].browse(old_ids)
            old_invoices.with_context(is_merge=True).action_invoice_cancel()

        # Make link between original sale order
        # None if sale is not installed
        invoice_line_obj = self.env['account.invoice.line']
        for new_invoice_id in invoices_info:
            if 'sale.order' in self.env.registry:
                sale_todos = old_invoices.mapped(
                    'invoice_line_ids.sale_line_ids.order_id')
                for org_so in sale_todos:
                    for so_line in org_so.order_line:
                        invoice_line = invoice_line_obj.search(
                            [('id', 'in', so_line.invoice_lines.ids),
                             ('invoice_id', '=', new_invoice_id)])
                        if invoice_line:
                            so_line.write(
                                {'invoice_lines': [(6, 0, invoice_line.ids)]})

        # recreate link (if any) between original analytic account line
        # (invoice time sheet for example) and this new invoice
        anal_line_obj = self.env['account.analytic.line']
        if 'invoice_id' in anal_line_obj._fields:
            for new_invoice_id in invoices_info:
                anal_todos = anal_line_obj.search(
                    [('invoice_id', 'in', invoices_info[new_invoice_id])])
                anal_todos.write({'invoice_id': new_invoice_id})

        for new_invoice in allnewinvoices:
            new_invoice.compute_taxes()

        return invoices_info
