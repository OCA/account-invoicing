# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning
from openerp.tools.float_utils import float_round as round
import openerp.addons.decimal_precision as dp


class sale_create_invoice_plan(models.TransientModel):
    _name = 'sale.create.invoice.plan'
    _description = 'Create Invoice Plan'

    @api.model
    def _default_order_amount(self):
        order = self.env['sale.order'].browse(self._context.get('active_id'))
        base_amount = order.price_include and \
            order.amount_total or order.amount_untaxed
        return base_amount

    use_deposit = fields.Boolean(
        string='Advance on 1st Invoice',
        default=False,
    )
    num_installment = fields.Integer(
        string='Number of Installment',
        default=0,
    )
    installment_ids = fields.One2many(
        'sale.create.invoice.plan.installment',
        'plan_id',
        string='Installments',
    )
    order_amount = fields.Float(
        string='Order Amount Untaxed',
        readonly=True,
        default=_default_order_amount,
    )
    invoice_mode = fields.Selection(
        [('change_price', 'As 1 Job (change price)'),
         ('change_quantity', 'As Units (change quantity)')
         ],
        string='Invoice Mode',
        required=True,
        default='change_price')

    @api.model
    def _check_deposit_account(self):
        prop = self.env['ir.property'].get(
            'property_account_deposit_customer', 'res.partner')
        prop_id = prop and prop.id or False
        account_id = self.env['account.fiscal.position'].map_account(prop_id)
        if not account_id:
            raise except_orm(
                _('Configuration Error!'),
                _('There is no deposit customer account '
                  'defined as global property.')
            )

    @api.model
    def _validate_total_amount(self):
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        amount_total = sum([x.installment > 0 and x.amount or
                            0.0 for x in self.installment_ids])
        if round(amount_total, prec) != round(self.order_amount, prec):
            raise except_orm(
                _('Amount Mismatch!'),
                _("Total installment amount %d not equal to order amount %d!")
                % (amount_total, self.order_amount))

    @api.one
    def do_create_invoice_plan(self):
        self._validate_total_amount()
        self.env['sale.invoice.plan']._validate_installment_date(
            self.installment_ids)
        order = self.env['sale.order'].browse(self._context['active_id'])
        order.invoice_plan_ids.unlink()
        lines = []
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        if self.use_deposit:
            self._check_deposit_account()
            base_amount = (order.price_include and
                           order.amount_total or order.amount_untaxed)
            lines.append({
                'order_id': order.id,
                'order_line_id': False,
                'installment': 0,
                'date_invoice': self.installment_ids[0].date_invoice,
                'deposit_percent': self.installment_ids[0].percent,
                'deposit_amount': round(self.installment_ids[0].percent/100 *
                                        base_amount, prec)
            })

        for install in self.installment_ids:
            if install.installment > 0:
                for order_line in order.order_line:
                    subtotal = order.price_include and \
                        (order_line.product_uom_qty *
                         order_line.price_unit) or order_line.price_subtotal
                    lines.append({
                        'order_id': order.id,
                        'order_line_id': order_line.id,
                        'installment': install.installment,
                        'date_invoice': install.date_invoice,
                        'invoice_percent': install.percent,
                        'invoice_amount': round(install.percent/100 *
                                                subtotal, prec),
                    })

        order.invoice_plan_ids = lines
        order.use_deposit = self.use_deposit
        order.invoice_mode = self.invoice_mode

    @api.onchange('use_deposit', 'num_installment')
    def _onchange_plan(self):
        order = self.env['sale.order'].browse(self._context.get('active_id'))
        i = 1
        if self.use_deposit:
            i = 0
        lines = []
        base_amount = order.price_include and \
            order.amount_total or order.amount_untaxed
        while i <= self.num_installment:
            lines.append({'installment': i,
                          'order_amount': base_amount,
                          'amount': i == 1 and base_amount or 0,
                          'percent': i == 1 and 100 or 0})
            i += 1
        self.installment_ids = False
        self.installment_ids = lines


class sale_create_invoice_plan_installment(models.TransientModel):
    _name = 'sale.create.invoice.plan.installment'
    _description = 'Create Invoice Plan Installments'

    plan_id = fields.Many2one(
        'sale.create.invoice.plan',
        string='Wizard Reference',
        readonly=True,
    )
    installment = fields.Integer(
        string='Installment',
        readonly=True,
        help="Group of installment. "
        "Each group will be an invoice",
    )
    date_invoice = fields.Date(
        string='Invoice Date',
        required=True,
        help="Invoice created for this installment will be using this date",
    )
    order_amount = fields.Float(
        string='Order Amount',
    )
    percent = fields.Float(
        string='%',
        digits=(16, 10),
    )
    amount = fields.Float(
        string='Amount',
        digits=dp.get_precision('Account'),
    )

    @api.onchange('percent')
    def _onchange_percent(self):
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        self.amount = round(self.order_amount * self.percent / 100, prec)

    @api.onchange('amount')
    def _onchange_amount(self):
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        if not self.order_amount:
            raise Warning(_('Order amount equal to 0.0!'))
        new_val = self.amount / self.order_amount * 100
        if round(new_val, prec) != round(self.percent, prec):
            self.percent = new_val

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
