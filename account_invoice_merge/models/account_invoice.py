# -*- coding: utf-8 -*-
# Copyright 2004-2010 Tiny SPRL (http://tiny.be).
# Copyright 2010-2011 Elico Corp.
# Copyright 2016 Acsone (https://www.acsone.eu/)
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, api
from openerp import workflow
from openerp.osv.orm import browse_record, browse_null
from openerp.tools import float_is_zero


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

        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'account_id'):
                    if not field_val:
                        field_val = False
                if (isinstance(field_val, browse_record) and
                        field != 'invoice_line_tax_ids' and
                        field != 'sale_line_ids'):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif (isinstance(field_val, list) or
                        field == 'invoice_line_tax_ids' or
                        field == 'sale_line_ids'):
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
                        (invoice_infos['name'] or '') + ' ' + \
                        account_invoice.name
                if account_invoice.origin and \
                        account_invoice.origin not in origins:
                    invoice_infos['origin'] = \
                        (invoice_infos['origin'] or '') + ' ' + \
                        account_invoice.origin
                    origins.add(account_invoice.origin)
                if account_invoice.reference \
                        and account_invoice.reference not in client_refs:
                    invoice_infos['reference'] = \
                        (invoice_infos['reference'] or '') + ' ' + \
                        account_invoice.reference
                    client_refs.add(account_invoice.reference)

            for invoice_line in account_invoice.invoice_line_ids:
                line_key = make_key(
                    invoice_line, self._get_invoice_line_key_cols())

                o_line = invoice_infos['invoice_line_ids'].\
                    setdefault(line_key, {})

                if o_line:
                    # merge the line with an existing line
                    o_line['quantity'] += invoice_line.quantity
                else:
                    # append a new "standalone" line
                    o_line['quantity'] = invoice_line.quantity

        allinvoices = []
        allnewinvoices = []
        invoices_info = {}
        qty_prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for invoice_key, (invoice_data, old_ids) in new_invoices.iteritems():
            # skip merges with only one invoice
            if len(old_ids) < 2:
                allinvoices += (old_ids or [])
                continue
            # cleanup invoice line data
            for key, value in invoice_data['invoice_line_ids'].iteritems():
                value.update(dict(key))

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
            # make triggers pointing to the old invoices point to the new
            # invoice
            for old_id in old_ids:
                workflow.trg_redirect(
                    self.env.uid, 'account.invoice', old_id, newinvoice.id,
                    self.env.cr)
                workflow.trg_validate(
                    self.env.uid, 'account.invoice', old_id, 'invoice_cancel',
                    self.env.cr)

        # Make link between original sale order
        # None if sale is not installed
        so_obj = self.env['sale.order'] \
            if 'sale.order' in self.env.registry else False
        invoice_line_obj = self.env['account.invoice.line']
        for new_invoice_id in invoices_info:
            if so_obj is not False:
                todos = so_obj.search(
                    [('invoice_ids', 'in', invoices_info[new_invoice_id])])
                todos.write({'invoice_ids': [(4, new_invoice_id)]})
                for org_so in todos:
                    for so_line in org_so.order_line:
                        invoice_lines = invoice_line_obj.search(
                            [('product_id', '=', so_line.product_id.id),
                             ('invoice_id', '=', new_invoice_id)])
                        if invoice_lines:
                            so_line.write(
                                {'invoice_lines': [(6, 0, invoice_lines.ids)]})

        # recreate link (if any) between original analytic account line
        # (invoice time sheet for example) and this new invoice
        anal_line_obj = self.env['account.analytic.line']
        if 'invoice_id' in anal_line_obj._columns:
            for new_invoice_id in invoices_info:
                todos = anal_line_obj.search(
                    [('invoice_id', 'in', invoices_info[new_invoice_id])])
                todos.write({'invoice_id': new_invoice_id})

        for new_invoice in allnewinvoices:
            new_invoice.compute_taxes()

        return invoices_info
