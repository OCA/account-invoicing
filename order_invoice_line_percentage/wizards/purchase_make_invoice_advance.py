# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class purchase_advance_payment_inv(osv.osv_memory):
    _name = "purchase.advance.payment.inv"
    _description = "Purchase Advance Payment Invoice"

    _columns = {
        'line_percent': fields.float(
            'Installment',
            digits_compute=dp.get_precision('Account'),
            help="The % of installment to be used to "
            "calculate the quantity to invoice"),
    }

    _defaults = {
        'amount': 0.0,
    }

    def create_invoices(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)
        # Additional case, Line Percentage
        if wizard.line_percent:
            # Getting PO Line IDs of this PO
            purchase_obj = self.pool.get('purchase.order')
            purchase_ids = context.get('active_ids', [])
            order = purchase_obj.browse(cr, uid, purchase_ids[0])

            if order.invoiced_rate + wizard.line_percent > 100:
                raise osv.except_osv(
                    _('Warning!'),
                    _('This percentage is too high, '
                      'it make overall invoiced rate exceed 100%!'))

            order_line_ids = []
            for order_line in order.order_line:
                order_line_ids.append(order_line.id)
            # Assign them into active_ids
            context.update({'active_ids': order_line_ids})
            context.update({'line_percent': wizard.line_percent})
            purchase_order_line_make_invoice_obj = self.pool.get(
                'purchase.order.line_invoice')
            res = purchase_order_line_make_invoice_obj.makeInvoices(
                cr, uid, ids, context=context)
            if not context.get('open_invoices', False):
                return {'type': 'ir.actions.act_window_close'}
            return res

        return super(purchase_advance_payment_inv, self).create_invoices(
            cr, uid, ids, context=context)

    def open_invoices(self, cr, uid, ids, invoice_ids, context=None):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(
            cr, uid, 'account', 'invoice_supplier_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(
            cr, uid, 'account', 'invoice_tree')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Advance Invoice'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'res_id': invoice_ids[0],
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': "{'type': 'in_invoice'}",
            'type': 'ir.actions.act_window',
        }

purchase_advance_payment_inv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
