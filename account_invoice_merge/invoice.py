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

from openerp.osv import orm, fields
import netsvc
from openerp.tools.translate import _
from openerp.osv.orm import browse_record, browse_null
import openerp.modules as addons


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def do_merge(self, cr, uid, ids, context=None):
        """
        To merge similar type of account invoices.
        Invoices will only be merged if:
        * Account invoices are in draft
        * Account invoices belong to the same partner
        * Account invoices are have same company, partner, address, currency, journal, currency, salesman, account, type
        Lines will only be merged if:
        * Invoice lines are exactly the same except for the quantity and unit

         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: the ID or list of IDs
         @param context: A standard dictionary

         @return: new account invoice id

        """
        wf_service = netsvc.LocalService("workflow")

        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'account_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

    # compute what the new invoices should contain

        new_invoices = {}

        for account_invoice in [invoice for invoice in self.browse(cr, uid, ids, context=context) if invoice.state == 'draft']:
            invoice_key = make_key(account_invoice, ('commercial_partner_id', 'user_id', 'type', 'account_id', 'currency_id', 'journal_id', 'company_id'))
            new_invoice = new_invoices.setdefault(invoice_key, ({}, []))
            new_invoice[1].append(account_invoice.id)
            invoice_infos = new_invoice[0]
            if not invoice_infos:
                invoice_infos.update({
                    'origin': '%s' % (account_invoice.origin or '',),
                    'partner_id': account_invoice.partner_id.id,
                    'commercial_partner_id':account_invoice.commercial_partner_id.id,
                    'journal_id': account_invoice.journal_id.id,
                    'user_id': account_invoice.user_id.id,
                    'currency_id': account_invoice.currency_id.id,
                    'company_id': account_invoice.company_id.id,
                    'type': account_invoice.type,
                    'account_id': account_invoice.account_id.id,
                    'state': 'draft',
                    'invoice_line': {},
                    'reference': '%s' % (account_invoice.reference or '',),
                    'name': '%s' % (account_invoice.name or '',),
                    'fiscal_position': account_invoice.fiscal_position and account_invoice.fiscal_position.id or False,
                    'period_id': account_invoice.period_id and account_invoice.period_id.id or False,
                })
            else:
                if account_invoice.name:
                    invoice_infos['name'] = (invoice_infos['name'] or '') + (' %s' % (account_invoice.name,))
                if account_invoice.origin:
                    invoice_infos['origin'] = (invoice_infos['origin'] or '') + ' ' + account_invoice.origin
                if account_invoice.reference:
                    invoice_infos['reference'] = (invoice_infos['reference'] or '') + (' %s' % (account_invoice.reference,))

            for invoice_line in account_invoice.invoice_line:
                line_key = make_key(invoice_line, ('name', 'origin', 'discount', 'invoice_line_tax_id', 'price_unit', 'product_id', 'account_id', 'account_analytic_id'))
                o_line = invoice_infos['invoice_line'].setdefault(line_key, {})
                if o_line:
                    # merge the line with an existing line
                    o_line['quantity'] += invoice_line.quantity * invoice_line.uos_id.factor / o_line['uom_factor']
                else:
                    # append a new "standalone" line
                    for field in ('quantity', 'uos_id'):
                        field_val = getattr(invoice_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line['uom_factor'] = invoice_line.uos_id and invoice_line.uos_id.factor or 1.0

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
            invoice_data['invoice_line'] = [(0, 0, value) for value in invoice_data['invoice_line'].itervalues()]

            # create the new invoice
            newinvoice_id = self.create(cr, uid, invoice_data)
            invoices_info.update({newinvoice_id: old_ids})
            allinvoices.append(newinvoice_id)

            # make triggers pointing to the old invoices point to the new invoice
            for old_id in old_ids:
                wf_service.trg_redirect(uid, 'account.invoice', old_id, newinvoice_id, cr)
                wf_service.trg_validate(uid, 'account.invoice', old_id, 'invoice_cancel', cr)

        # make link between original sale order or purchase order
        
        loaded_mods = addons.module.loaded
        so_obj, po_obj = None, None
        if 'sale' in loaded_mods:
            so_obj = self.pool.get('sale.order')
        if 'purchase' in loaded_mods:
            po_obj = self.pool.get('purchase.order')
        for new_invoice in invoices_info:
            if so_obj:
                todo_ids = so_obj.search(cr, uid, [('invoice_ids', 'in', invoices_info[new_invoice])], context=context)
                for org_order in so_obj.browse(cr, uid, todo_ids, context=context):
                    so_obj.write(cr, uid, [org_order.id], {'invoice_ids': [(4, new_invoice)]}, context)
            if po_obj:
                todo_ids = po_obj.search(cr, uid, [('invoice_ids', 'in', invoices_info[new_invoice])], context=context)
                for org_order in po_obj.browse(cr, uid, todo_ids, context=context):
                    po_obj.write(cr, uid, [org_order.id], {'invoice_ids': [(4, new_invoice)]}, context)
        # print invoices_info
        return invoices_info

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
