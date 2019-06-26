# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
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
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'account.billing'),
        index=True,
        help='Leave this field empty if this route is shared \
            between all companies'
    )
    date = fields.Date(
        string='Billing Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today,
        help='Effective date for accounting entries',
        track_visibility='always',
    )
    due_date = fields.Date(
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: fields.Date.context_today(self),
        required=True,
        track_visibility='always',
    )
    invoice_ids = fields.One2many(
        comodel_name='account.invoice',
        inverse_name='billing_id',
        string='Invoices',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self._context.get('active_ids', []),
    )
    invoice_related_count = fields.Integer(
        string='# of Invoices',
        compute='_compute_invoice_related_count',
        help='Count invoice in billing',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('billed', 'Billed')],
        string='Status',
        readonly=True,
        default='draft',
        help="""
            * The 'Draft' status is used when a user create a new billing\n
            * The 'Billed' status is used when user confirmed billing,
                billing number is generated\n
            * The 'Cancelled' status is used when user billing is cancelled
        """,
    )
    narration = fields.Text(
        string='Notes',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Notes',
    )
    bill_type = fields.Selection(
        [('out_invoice', 'Customer Invoice'),
         ('in_invoice', 'Vendor Bill')],
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
        help='Currency',
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(AccountBilling, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if res and view_type in ['tree', 'form']:
            invoices = self.env['account.invoice'].browse(
                self._context.get('active_ids', []))
            billing = invoices.mapped('billing_id')
            if any(inv.state != 'open' for inv in invoices):
                raise ValidationError(_('The billing cannot be processed '
                                        'because the invoice is not open!'))
            if billing:
                raise ValidationError(_(
                    'Invoice: %s, already billed!') % ', '.join(
                    invoices.filtered(lambda l: l.billing_id).mapped('number')
                    ))
        return res

    @api.onchange('bill_type')
    def _onchange_bill_type(self):
        # Set partner_id domain
        if self.bill_type:
            return {'domain': {'partner_id': [
                (MAP_INVOICE_TYPE_PARTNER_TYPE[self.bill_type], '=', True)]}}

    @api.multi
    def _get_partner_id(self):
        partner_ids = self.env['account.invoice'].browse(
            self._context.get('active_ids', [])).mapped('partner_id')
        if len(partner_ids) > 1:
            raise ValidationError(
                _('Please select invoices with same partner'))
        return partner_ids

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
        for billing in self:
            invoice_ids = self.env['account.invoice'].search_count([
                ('id', 'in', billing.invoice_ids.ids)
            ])
            billing.invoice_related_count = invoice_ids

    @api.multi
    def name_get(self):
        result = []
        for billing in self:
            result.append((billing.id, (billing.name or 'Draft')))
        return result

    @api.multi
    def validate_billing(self):
        for rec in self:
            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_('Billing cannot be processed because \
                    some invoices are not in state Open'))
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
            invoice_paid = rec.invoice_ids.filtered(
                lambda l: l.state == 'paid')
            if invoice_paid:
                raise ValidationError(_("Invoice paid already."))
            rec.write({'state': 'cancel'})
            rec.invoice_ids.write({'billing_id': False})
            self.message_post(body=_('Billing %s is cancelled') % rec.name)
        return True

    @api.multi
    def invoice_relate_billing_tree_view(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        result.update({'domain': [('id', 'in', self.invoice_ids.ids)]})
        return result
