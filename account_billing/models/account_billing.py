# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'in_invoice': 'supplier',
}


class AccountBilling(models.Model):
    _name = 'account.billing'
    _description = 'Account Billing'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    name = fields.Char(
        readonly=True,
        copy=False,
        help='Number of account.billing',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        required=True,
        default=lambda self: self._get_partner_id(),
        help='Partner Information',
        track_visibility='always',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'account.billing'),
        index=True,
        help='Leave this field empty if this route is shared \
            between all companies',
    )
    date = fields.Date(
        string='Billing Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today,
        help='Effective date for accounting entries',
        track_visibility='always',
    )
    threshold_date = fields.Date(
        readonly=True,
        states={'draft': [('readonly', False)]},
        string='Threshold Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        track_visibility='always',
    )
    invoice_related_count = fields.Integer(
        string='# of Invoices',
        compute='_compute_invoice_related_count',
        help='Count invoice in billing',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('billed', 'Billed'),
        ],
        string='Status',
        readonly=True,
        default='draft',
        help='''
            * The 'Draft' status is used when a user create a new billing\n
            * The 'Billed' status is used when user confirmed billing,
                billing number is generated\n
            * The 'Cancelled' status is used when user billing is cancelled
        ''',
    )
    narration = fields.Text(
        string='Notes',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Notes',
    )
    bill_type = fields.Selection(
        selection=[
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Vendor Bill'),
        ],
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self._context.get('bill_type', False),
        help='Type of invoice',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self._get_currency_id(),
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Currency',
    )
    billing_line_ids = fields.One2many(
        comodel_name='account.billing.line',
        inverse_name='billing_id',
        string='Bill Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    threshold_date_type = fields.Selection(
        selection=[
            ('date_due', 'Due Date'),
            ('date_invoice', 'Invoice Date'),
        ],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='date_due',
    )

    @api.multi
    def _get_invoices(self, date=False, types=False):
        invoices = self.env['account.invoice'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'open'),
            ('currency_id', '=', self.currency_id.id),
            (date, '<=', self.threshold_date),
            ('type', 'in', types),
        ])
        return invoices

    @api.onchange(
        'partner_id', 'currency_id',
        'threshold_date', 'threshold_date_type')
    def _onchange_invoice_list(self):
        self.billing_line_ids = False
        Billing_line = self.env['account.billing.line']
        invoices = self.env['account.invoice'].browse(
            self._context.get('active_ids', []))
        if not invoices:
            types = ['in_invoice', 'in_refund']
            if self.bill_type == 'out_invoice':
                types = ['out_invoice', 'out_refund']
            invoices = self._get_invoices(self.threshold_date_type, types)
        for line in invoices:
            if line.type in ['out_refund', 'in_refund']:
                line.residual = line.residual*(-1)
            self.billing_line_ids += Billing_line.new({
                'invoice_id': line.id, 'total': line.residual
            })

    @api.onchange('bill_type')
    def _onchange_bill_type(self):
        # Set partner_id domain
        if self.bill_type:
            return {'domain': {'partner_id': [
                (MAP_INVOICE_TYPE_PARTNER_TYPE[self.bill_type], '=', True)]}}

    @api.multi
    def _get_partner_id(self):
        inv_ids = self.env['account.invoice'].browse(
            self._context.get('active_ids', []))
        if any(inv.state != 'open' for inv in inv_ids):
            raise ValidationError(_('Billing cannot be processed because \
                some invoices are not in state Open'))
        partners = self.env['account.invoice'].browse(
            self._context.get('active_ids', [])).mapped('partner_id')
        if len(partners) > 1:
            raise ValidationError(
                _('Please select invoices with same partner'))
        return partners and partners[0] or False

    @api.multi
    def _get_currency_id(self):
        currency_ids = self.env['account.invoice'].browse(
            self._context.get('active_ids', [])).mapped('currency_id')
        if len(currency_ids) > 1:
            raise ValidationError(
                _('Please select invoices with same currency'))
        return currency_ids or self.env.user.company_id.currency_id

    @api.multi
    def _compute_invoice_related_count(self):
        self.invoice_related_count = len(self.billing_line_ids)

    @api.multi
    def name_get(self):
        result = [(billing.id, (billing.name or 'Draft')) for billing in self]
        return result

    @api.multi
    def validate_billing(self):
        for rec in self:
            date_type = dict(self._fields['threshold_date_type'].selection).\
                get(self.threshold_date_type)
            if any(rec.threshold_date < (b.threshold_date if
                   self.threshold_date_type == 'date_due' else b.invoice_date)
                   for b in rec.billing_line_ids):
                raise ValidationError(
                    _('Threshold Date cannot be later than the %s in lines')
                    % (date_type))
            # keep the number in case of a billing reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.bill_type == 'out_invoice':
                    sequence_code = 'account.customer.billing'
                if rec.bill_type == 'in_invoice':
                    sequence_code = 'account.supplier.billing'
                rec.name = self.env['ir.sequence'].with_context(
                    ir_sequence_date=rec.date).next_by_code(sequence_code)
            rec.write({'state': 'billed'})
            rec.message_post(body=_('Billing is billed.'))
        return True

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})
            rec.message_post(body=_('Billing is reset to draft'))
        return True

    @api.multi
    def action_cancel(self):
        for rec in self:
            # vals = [rec.invoice_id for rec in self.billing_line_ids]
            invoice_paid = rec.billing_line_ids.mapped('invoice_id').filtered(
                lambda l: l.state == 'paid')
            if invoice_paid:
                raise ValidationError(_('Invoice paid already.'))
            rec.write({'state': 'cancel'})
            self.message_post(body=_('Billing %s is cancelled') % rec.name)
        return True

    @api.multi
    def invoice_relate_billing_tree_view(self):
        self.ensure_one()
        if self.bill_type == 'out_invoice':
            action = self.env.ref('account.action_invoice_tree1')
        if self.bill_type == 'in_invoice':
            action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        vals = [rec.invoice_id.id for rec in self.billing_line_ids]
        result.update({'domain': [('id', 'in', vals)]})
        return result


class AccountBillingLine(models.Model):
    _name = 'account.billing.line'
    _description = 'Billing Line'

    billing_id = fields.Many2one(
        comodel_name='account.billing',
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
    )
    number = fields.Char(related='invoice_id.number')
    invoice_date = fields.Date(related='invoice_id.date_invoice')
    threshold_date = fields.Date(related='invoice_id.date_due')
    origin = fields.Char(related='invoice_id.origin')
    total = fields.Float()
    state = fields.Selection(related='invoice_id.state')
