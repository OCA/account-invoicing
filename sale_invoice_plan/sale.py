# -*- coding: utf-8 -*-
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp import models, fields, api, _
from openerp.exceptions import except_orm
from openerp.tools.float_utils import float_round as round
from openerp import workflow
import time
import logging

_logger = logging.getLogger(__name__)


class sale_order(models.Model):

    _inherit = 'sale.order'

    use_invoice_plan = fields.Boolean(
        string='Use Invoice Plan',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=False,
        help="It indicates that the invoice has been sent.",
    )
    invoice_plan_ids = fields.One2many(
        'sale.invoice.plan',
        'order_id',
        string='Invoice Plan',
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'invoice_except': [('readonly', False)]},
    )
    invoice_plan_wd_ids = fields.One2many(
        'sale.invoice.plan',
        'order_id',
        string='Invoice Plan with Advance',
        copy=True,
    )
    use_deposit = fields.Boolean(
        string='Advance on 1st Invoice',
        readonly=True,
    )
    invoice_mode = fields.Selection(
        [('change_price', 'As 1 Job (change price)'),
         ('change_quantity', 'As Units (change quantity)')],
        string='Invoice Mode',
        requied=True,
        readonly=True,
    )

    @api.model
    def _calculate_subtotal(self, vals):
        if vals.get('invoice_plan_ids', False) or \
                vals.get('invoice_plan_wd_ids', False):
            plan_ids = self.invoice_plan_ids or self.invoice_plan_wd_ids
            old_installment = 0
            subtotal = 0.0
            index_list = []  # Keep the subtotal line index
            i = 0
            for line in plan_ids:
                if line.installment > old_installment:  # Start new installment
                    if len(index_list) > 0:
                        del index_list[-1]  # Remove last index
                    subtotal = 0.0
                index_list.append(i)
                if line.installment == 0:
                    line.subtotal = 0.0
                else:
                    subtotal += line.invoice_amount
                    line.subtotal = subtotal
                old_installment = line.installment
                i += 1
            if len(index_list) > 0:
                del index_list[-1]
            # Now, delete subtotal  not in the index_list
            for i in index_list:
                self.invoice_plan_ids[i].subtotal = 0.0

    @api.model
    def _validate_invoice_plan(self, vals):
        if vals.get('invoice_plan_ids', False):
            for line in vals.get('invoice_plan_ids'):
                # Deleting (2) line that is not being cancelled
                plan = self.env['sale.invoice.plan'].browse(line[1])
                if line[0] == 2:  # Deletion
                    plan = self.env['sale.invoice.plan'].browse(line[1])
                    if plan.state and plan.state != 'cancel':
                        raise except_orm(
                            _('Delete Error!'),
                            _("You are trying deleting line(s) "
                              "that has not been cancelled!\n"
                              "Please discard change and try again!"))

    # Don't know why, but can't use v8 API !!, so revert to v7
    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        order_id = super(sale_order, self).copy(cr, uid, id,
                                                default, context)
        order = self.browse(cr, uid, order_id)
        for invoice_plan in order.invoice_plan_ids:
            copy_to_line_id = invoice_plan.order_line_id and \
                invoice_plan.order_line_id.copy_to_line_id.id
            self.pool.get('sale.invoice.plan').write(
                cr, uid, [invoice_plan.id],
                {'order_line_id': copy_to_line_id}, context)
        return order_id

    @api.multi
    def write(self, vals):
        for sale in self:
            sale._validate_invoice_plan(vals)
        res = super(sale_order, self).write(vals)
        for sale in self:
            sale._calculate_subtotal(vals)
        self.env['sale.invoice.plan']._validate_installment_date(
            self.invoice_plan_ids)
        return res

    @api.onchange('use_invoice_plan')
    def _onchange_use_invoice_plan(self):
        if self.use_invoice_plan:
            self.order_policy = 'manual'
        else:
            default_order_policy = self.env['ir.values'].get_default(
                'sale.order', 'order_policy')
            self.order_policy = default_order_policy or 'manual'

    @api.one
    def _check_invoice_plan(self):
        if self.use_invoice_plan:
            obj_precision = self.env['decimal.precision']
            prec = obj_precision.precision_get('Account')
            for order_line in self.order_line:
                subtotal = self.price_include and \
                    order_line.product_uom_qty * order_line.price_unit or \
                    order_line.price_subtotal
                invoice_lines = self.env['sale.invoice.plan'].search(
                    [('order_line_id', '=', order_line.id)])
                total_amount = 0.0
                for line in invoice_lines:
                    total_amount += line.invoice_amount
                    # Validate percent
                    if round(line.invoice_percent/100 * subtotal, prec) != \
                            round(line.invoice_amount, prec):
                        raise except_orm(
                            _('Invoice Plan Percent Mismatch!'),
                            _("%s on installment %s")
                            % (order_line.name, line.installment))
                if round(total_amount, prec) != round(subtotal, prec):
                    raise except_orm(
                        _('Invoice Plan Amount Mismatch!'),
                        _("%s, plan amount %d not equal to line amount %d!")
                        % (order_line.name, total_amount, subtotal))
        return True

    @api.multi
    def action_button_confirm(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        self._check_invoice_plan()
        super(sale_order, self).action_button_confirm()
        return True

    @api.multi
    def action_cancel_draft_invoices(self):
        assert len(self) == 1, \
            'This option should only be used for a single id at a time.'
        # Get all unpaid invoice
        for invoice in self.invoice_ids:
            if invoice.state in ('draft'):
                workflow.trg_validate(
                    self._uid, 'account.invoice',
                    invoice.id, 'invoice_cancel', self._cr)
        return True

    @api.multi
    def _create_deposit_invoice(self, percent, amount, date_invoice=False):
        for order in self:
            if amount:
                advance_label = 'Advance'
                prop = self.env['ir.property'].get(
                    'property_account_deposit_customer', 'res.partner')
                prop_id = prop and prop.id or False
                account_id = self.env[
                    'account.fiscal.position'].map_account(prop_id)
                name = _("%s of %s %%") % (advance_label, percent)
                # create the invoice
                inv_line_values = {
                    'name': name,
                    'origin': order.name,
                    'user_id': order.user_id.id,
                    'account_id': account_id,
                    'price_unit': amount,
                    'quantity': 1.0,
                    'discount': False,
                    'uos_id': False,
                    'product_id': False,
                    'invoice_line_tax_id': [
                        (6, 0, [x.id for x in order.order_line[0].tax_id])],
                    'account_analytic_id': order.project_id.id or False,
                }
                inv_values = self._prepare_invoice(order, inv_line_values)
                inv_values.update({'is_deposit': True,
                                   'date_invoice': date_invoice})
                # Chainging from [6, 0, ...] to [0, 0, ...]
                inv_values['invoice_line'] = [
                    (0, 0, inv_values['invoice_line'][0][2])]
                inv_id = self.env[
                    'sale.advance.payment.inv']._create_invoices(inv_values,
                                                                 self.id)
                # Calculate due date
                invoice = self.env['account.invoice'].browse(inv_id)
                if date_invoice:
                    data = invoice.onchange_payment_term_date_invoice(
                        order.payment_term.id, date_invoice)
                else:
                    data = invoice.onchange_payment_term_date_invoice(
                        order.payment_term.id,
                        time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                if data.get('value', False):
                    invoice.write(data['value'])
                return inv_id
        return False

    @api.multi
    def action_invoice_create(self, grouped=False,
                              states=None, date_invoice=False):
        self._check_invoice_plan()
        # Mixed Invoice plan and grouping is not allowed.
        if grouped and (True in [order.use_invoice_plan for order in self]):
            raise except_orm(
                _('Warning'),
                _("Mix order and order with invoice plan is not allowed!"))
        # Case use_invoice_plan, create multiple invoice by installment
        for order in self:
            if order.use_invoice_plan:
                plan_obj = self.env['sale.invoice.plan']
                installments = list(set([plan.installment
                                         for plan in order.invoice_plan_ids]))
                for installment in installments:
                    # Getting invoice plan for each installment
                    blines = plan_obj.search(
                        [('installment', '=', installment),
                         ('order_id', '=', order.id),
                         ('state', 'in', [False, 'cancel'])])
                    if blines:
                        if installment == 0:  # Deposit Case
                            inv_id = self._create_deposit_invoice(
                                blines[0].deposit_percent,
                                blines[0].deposit_amount,
                                blines[0].date_invoice)
                            blines.write({'ref_invoice_id': inv_id})
                        else:
                            percent_dict = {}
                            date_invoice = (blines and
                                            blines[0].date_invoice or
                                            False)
                            for b in blines:
                                percent_dict.update(
                                    {b.order_line_id: b.invoice_percent})
                            order = order.with_context(
                                installment=installment,
                                invoice_plan_percent=percent_dict)
                            inv_id = super(
                                sale_order, order).action_invoice_create(
                                    grouped=grouped,
                                    states=states,
                                    date_invoice=date_invoice)
                            blines.write({'ref_invoice_id': inv_id})
            else:
                inv_id = super(sale_order, order).action_invoice_create(
                    grouped=grouped, states=states, date_invoice=date_invoice)
        return inv_id

    @api.model
    def _make_invoice(self, order, lines):
        inv_id = super(sale_order, self)._make_invoice(order, lines)
        if order.use_invoice_plan:
            invoice = self.env['account.invoice'].browse(inv_id)
            for line in invoice.invoice_line:
                if line.price_unit < 0:  # Remove line with negative price line
                    line.unlink()
            for deposit_inv in order.invoice_ids:
                if deposit_inv.state not in ('cancel',) and \
                        deposit_inv.is_deposit:
                    for preline in deposit_inv.invoice_line:
                        ratio = (order.amount_untaxed and
                                 (invoice.amount_untaxed /
                                  order.amount_untaxed) or 1.0)
                        inv_line = preline.copy(
                            {'invoice_id': inv_id,
                             'price_unit': -preline.price_unit})
                        inv_line.quantity = inv_line.quantity * ratio
            invoice.button_compute()
        return inv_id

    @api.multi
    def manual_invoice(self, context=None):
        # If use_invoice_plan, view invoices in list view.
        res = super(sale_order, self).manual_invoice()
        if self[0].use_invoice_plan:
            res = self.action_view_invoice()
        return res


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    invoice_plan_ids = fields.One2many(
        'sale.invoice.plan',
        'order_line_id',
        string='Invoice Plan',
        readonly=True,
    )
    copy_from_line_id = fields.Many2one(
        'sale.order.line',
        string="Copied from",
        readonly=True,
    )
    copy_to_line_id = fields.Many2one(
        'sale.order.line',
        string="Last copied to",
        readonly=True,
    )

    def copy_data(self, cr, uid, id, default=None, context=None):
        default = dict(default or {})
        default.update({'copy_from_line_id': id, 'copy_to_line_id': False})
        return super(sale_order_line, self).copy_data(cr, uid, id,
                                                      default, context=context)

    @api.model
    def create(self, vals):
        new_line = super(sale_order_line, self).create(vals)
        if new_line.copy_from_line_id:
            old_line = self.browse(new_line.copy_from_line_id.id)
            old_line.copy_to_line_id = new_line.id
        return new_line

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        # Call super
        res = super(sale_order_line, self).\
            _prepare_order_line_invoice_line(line, account_id)
        # For invoice plan
        invoice_plan_percent = self._context.get('invoice_plan_percent', False)
        if not res and invoice_plan_percent:  # But if invoice plan, try again
            res = self._prepare_order_line_invoice_line_hook(line, account_id)
        if invoice_plan_percent:
            if line in invoice_plan_percent:
                if line.order_id.invoice_mode == 'change_quantity':
                    res.update({'quantity': (res.get('quantity') or 0.0) *
                                (line and invoice_plan_percent[line] or 0.0) /
                                100})
                elif line.order_id.invoice_mode == 'change_price':
                    res.update({'price_unit': (res.get('price_unit') or 0.0) *
                                (res.get('quantity') or 0.0) *
                                (line and invoice_plan_percent[line] or 0.0) /
                                100,
                                'quantity': 1.0})
            else:
                return False
        # From invoice_percentage,
        line_percent = self._context.get('line_percent', False)
        if line_percent:
            res.update({'quantity': ((res.get('quantity') or 0.0) *
                                     (line_percent / 100))})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
