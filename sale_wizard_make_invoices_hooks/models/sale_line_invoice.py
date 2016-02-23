# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.tools.translate import _
from openerp import workflow


class sale_order_line_make_invoice(osv.osv_memory):

    _inherit = "sale.order.line.make.invoice"

    def _sale_order_line_make_invoice_hook1(self, cr, uid, res, order):
        return

    # Overwrite just to pass context (nstda)
    def make_invoices(self, cr, uid, ids, context=None):
        """
             To make invoices.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: A dictionary which of fields with values.

        """
        if context is None:
            context = {}
        res = False
        invoices = {}

    # TODO: merge with sale.py/make_invoice
        def make_invoice(order, lines):
            """
                 To make invoices.

                 @param order:
                 @param lines:

                 @return:

            """
            inv = self._prepare_invoice(cr, uid, order, lines)
            inv_id = self.pool.get('account.invoice').create(cr, uid, inv)
            return inv_id

        sales_order_line_obj = self.pool.get('sale.order.line')
        sales_order_obj = self.pool.get('sale.order')
        for line in sales_order_line_obj.browse(
                cr, uid, context.get('active_ids', []), context=context):
            if (not line.invoiced) and (line.state not in ('draft', 'cancel')):
                if line.order_id not in invoices:
                    invoices[line.order_id] = []
                # HOOK, pass context
                line_id = sales_order_line_obj.invoice_line_create(
                    cr, uid, [line.id], context=context)
                # --
                for lid in line_id:
                    invoices[line.order_id].append(lid)
        for order, il in invoices.items():
            res = make_invoice(order, il)
            # HOOK
            self._sale_order_line_make_invoice_hook1(cr, uid, res, order)
            # --
            cr.execute('INSERT INTO sale_order_invoice_rel \
                    (order_id,invoice_id) values (%s,%s)', (order.id, res))
            sales_order_obj.invalidate_cache(
                cr, uid, ['invoice_ids'], [order.id], context=context)
            flag = True
            sales_order_obj.message_post(
                cr, uid, [order.id],
                body=_("Invoice created"), context=context)
            data_sale = sales_order_obj.browse(
                cr, uid, order.id, context=context)
            for line in data_sale.order_line:
                if not line.invoiced:
                    flag = False
                    break
            if flag:
                sales_order_obj.write(
                    cr, uid, [order.id], {'state': 'progress'})
                workflow.trg_validate(
                    uid, 'sale.order', order.id, 'manual_invoice', cr)
        if not invoices:
            raise osv.except_osv(_('Warning!'), _(
                'Invoice cannot be created for this Sales Order Line due '
                'to one of the following reasons:\n1.The state of this sales '
                'order line is either "draft" or "cancel"!\n2.The Sales Order '
                'Line is Invoiced!'))
        if context.get('open_invoices', False):
            return self.open_invoices(cr, uid, ids, res, context=context)
        # HOOK, refresh, for case not open invoice.
        self.pool.get('account.invoice').button_compute(
            cr, uid, [res], context=context)
        # --
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
