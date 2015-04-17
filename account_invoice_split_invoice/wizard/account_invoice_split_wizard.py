# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import netsvc


class split_invoice_wizard(orm.TransientModel):
    """Wizard for selecting invoice lines to be moved
    onto a new invoice."""
    _name = 'account.invoice.split.wizard'

    def _get_invoice_id(self, cr, uid, context=None):
        return context.get('active_id')

    def _get_default_ids(self, cr, uid, context=None):
        return self._get_invoice_line_ids(cr, uid, [0], 'invoice_line_ids',
                                          '', context)[0]

    def _get_invoice_line_ids(self, cr, uid, ids, field_name, arg, context):
        active_id = context.get('active_id')
        invoice = self.pool.get('account.invoice').browse(cr, uid, active_id,
                                                          context)
        line_ids = [line.id for line in invoice.invoice_line]
        return {id: line_ids for id in ids}

    def _write_lines(self, cr, uid, ids, field_name, field_value, arg,
                     context):
        """Update invoice_lines. Those that have the invoice_id removed
        are attached to a new draft invoice."""
        if not isinstance(ids, list):
            ids = [ids]
        inv_line_obj = self.pool.get('account.invoice.line')
        inv_lines_to_update = list()
        inv_lines_vals = dict()
        for line in field_value:
            if line[0] == 1:  # one2many update
                inv_line_id = line[1]
                line_values = line[2]
                if line_values.get('split'):
                    # The line will be attached in a new invoice
                    inv_lines_to_update.append(inv_line_id)
                    invoice_id = inv_lines_vals.get('invoice_id')
                    if not invoice_id:
                        invoice_id = self._copy_invoice(cr, uid, ids, context)
                        inv_lines_vals['invoice_id'] = invoice_id
        if inv_lines_to_update:
            old_invoice = self.browse(cr, uid, ids[0], context).invoice_id
            inv_line_obj.write(cr, uid, inv_lines_to_update, inv_lines_vals)
            if old_invoice.state == 'open':
                # Cancel and validate again invoices
                self.pool.get('account.invoice').action_cancel(
                    cr, uid, [old_invoice.id], context=context)
                self.pool.get('account.invoice').action_cancel_draft(
                    cr, uid, [old_invoice.id])
                wf_service = netsvc.LocalService('workflow')
                wf_service.trg_validate(
                    uid, 'account.invoice', old_invoice.id, 'invoice_open', cr)
                wf_service.trg_validate(
                    uid, 'account.invoice', invoice_id, 'invoice_open', cr)
        return True

    def _copy_invoice(self, cr, uid, ids, context=None):
        # Create new invoice
        invoice_obj = self.pool.get('account.invoice')
        old_invoice = self.browse(cr, uid, ids[0], context).invoice_id
        invoice_obj.copy(cr, uid, old_invoice.id, {
            'date_invoice': old_invoice.date_invoice})
        found_ids = invoice_obj.search(cr, uid, [
            ('partner_id', '=', old_invoice.partner_id.id),
            ('date_invoice', '=', old_invoice.date_invoice),
            ('state', '=', 'draft')], context=context)
        if found_ids and len(found_ids) == 1:
            # Empty the new invoice
            inv_line_obj = self.pool.get('account.invoice.line')
            line_ids = inv_line_obj.search(cr, uid, [
                ('invoice_id', '=', found_ids[0])], context=context)
            inv_line_obj.unlink(cr, uid, line_ids, context)
            return found_ids[0]
        else:
            raise orm.except_orm(
                _('New invoice not found'),
                _('The new invoice was not found so the process was '
                  'cancelled.'))

    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'invoice_line_ids': fields.function(
            _get_invoice_line_ids, fnct_inv=_write_lines, type='one2many',
            obj='account.invoice.line', method=True,
            string=_('Invoice lines')),
    }

    _defaults = {
        'invoice_id': _get_invoice_id,
        'invoice_line_ids': _get_default_ids,
    }

    def split_invoice(self, cr, uid, ids, context=None):
        # Nothing to do here
        return True
