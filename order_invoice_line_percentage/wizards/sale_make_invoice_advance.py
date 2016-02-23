# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"

    def _get_advance_payment_method(self, cr, uid, context=None):
        res = []
        if context.get('active_model', False) == 'sale.order':
            sale_id = context.get('active_id', False)
            if sale_id:
                sale = self.pool.get('sale.order').browse(cr, uid, sale_id)
                valid_invoice = 0
                is_deposit = False
                for i in sale.invoice_ids:
                    if i.state not in ['cancel']:
                        valid_invoice += 1
                        if i.is_deposit:
                            is_deposit = True
                if sale.order_policy == 'manual':
                    if not valid_invoice:
                        res = [('all', 'Invoice the whole sales order'),
                               ('percentage', '1st Invoice Advance (%)'),
                               ('fixed', '1st Invoice Advance (Amt.)'),
                               ('line_percentage', 'Line Percentage')]
                    elif valid_invoice == 1 and is_deposit:
                        res = [('all', 'Invoice the whole sales order'),
                               ('line_percentage', 'Line Percentage')]
                    elif valid_invoice > 1 and is_deposit:
                        res = [('line_percentage', 'Line Percentage')]
                    elif valid_invoice:
                        res = [('line_percentage', 'Line Percentage')]

        return res

    _columns = {
        'line_percent': fields.float(
            'Installment', digits_compute=dp.get_precision('Account'),
            help="The % of installment to be used to "
            "calculate the quantity to invoice"),
        'advance_payment_method': fields.selection(
            _get_advance_payment_method,
            'What do you want to invoice?', required=True,),
    }
    _defaults = {
        'advance_payment_method': lambda self, cr, uid, c:
        self._get_advance_payment_method(cr, uid, context=c)[0][0],
    }

    def _translate_advance(self, cr, uid, percentage=False, context=None):
        return _("Advance of %s %%") if percentage else _("Advance of %s %s")

    # The original do not allow having tax in this advance.
    # But we also have to make sure
    # there are no more than 1 tax type.
    def _prepare_advance_invoice_vals(self, cr, uid, ids, context=None):
        res = super(
            sale_advance_payment_inv, self)._prepare_advance_invoice_vals(
            cr, uid, ids, context=context)
        sale_obj = self.pool.get('sale.order')
        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        wizard = self.browse(cr, uid, ids[0], context)
        sale_ids = context.get('active_ids', [])
        # Prepare corrections values
        accounts = {}
        amounts = {}
        taxes = {}
        for sale in sale_obj.browse(cr, uid, sale_ids, context=context):
            if not wizard.product_id.id:
                prop = ir_property_obj.get(
                    cr, uid,
                    'property_account_deposit_customer',
                    'res.partner', context=context)
                prop_id = prop and prop.id or False
                account_id = fiscal_obj.map_account(
                    cr, uid, sale.fiscal_position or False, prop_id)
                if not account_id:
                    raise osv.except_osv(
                        _('Configuration Error!'),
                        _('No advance account defined as global property.'))
                accounts[sale.id] = account_id
            if wizard.advance_payment_method == 'percentage':
                base_amount = sale.price_include and \
                    sale.amount_total or sale.amount_untaxed
                amounts[sale.id] = base_amount * wizard.amount / 100
            if not wizard.product_id:
                taxes[sale.id] = [
                    (6, 0, [x.id for x in sale.order_line[0].tax_id])]

            # Change values
            for sale_inv in res:
                if sale.id == sale_inv[0]:
                    sale_inv[1].update({'is_deposit': True})
                    invoice_line = sale_inv[1]['invoice_line']
                    if invoice_line:
                        if accounts.get(sale.id, False):
                            invoice_line[0][2][
                                'account_id'] = accounts.get(sale.id)
                        if amounts.get(sale.id, False):
                            invoice_line[0][2][
                                'price_unit'] = amounts.get(sale.id)
                        if taxes.get(sale.id, False):
                            invoice_line[0][2][
                                'invoice_line_tax_id'] = taxes.get(sale.id)

        return res

    def create_invoices(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)
        # Additional case, Line Percentage
        if wizard.advance_payment_method == 'line_percentage':
            if not wizard.line_percent:
                raise osv.except_osv(
                    _('Warning!'), _('You did not specify installment!'))
            # Getting Sale Order Line IDs of this SO
            sale_obj = self.pool.get('sale.order')
            sale_ids = context.get('active_ids', [])
            order = sale_obj.browse(cr, uid, sale_ids[0])
            order_line_ids = []

            if order.invoiced_rate + wizard.line_percent > 100:
                raise osv.except_osv(
                    _('Warning!'),
                    _('This percentage is too high, it make overall '
                      'invoiced rate exceed 100%!'))

            for order_line in order.order_line:
                order_line_ids.append(order_line.id)
            # Assign them into active_ids
            context.update({'active_ids': order_line_ids})
            context.update({'line_percent': wizard.line_percent})
            sale_order_line_make_invoice_obj = self.pool.get(
                'sale.order.line.make.invoice')
            res = sale_order_line_make_invoice_obj.make_invoices(
                cr, uid, ids, context=context)
            # Update invoice
            if res.get('res_id'):
                self.pool.get('account.invoice').button_compute(
                    cr, uid, [res.get('res_id')], context=context)
            return res
        else:
            return super(sale_advance_payment_inv, self).create_invoices(
                cr, uid, ids, context=context)

sale_advance_payment_inv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
