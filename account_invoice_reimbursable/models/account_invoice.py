# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    reimbursable_ids = fields.One2many(
        'account.invoice.reimbursable',
        inverse_name='invoice_id',
        readonly=True, copy=True,
        states={'draft': [('readonly', False)]},
    )
    reimbursable_count = fields.Integer(
        compute='_compute_reimbursable_count'
    )
    reimbursable_total = fields.Monetary(
        string='Total reimbursable', store=True, readonly=True,
        compute='_compute_reimbursable_amount')
    reimbursable_total_signed = fields.Monetary(
        string='Total reimbursable in Invoice Currency',
        currency_field='currency_id',
        store=True, readonly=True,
        compute='_compute_reimbursable_amount',
        help="Total reimbursable amount in the currency of the invoice, "
             "negative for credit notes.")
    reimbursable_total_company_signed = fields.Monetary(
        string='Total reimbursable in Company Currency',
        currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_reimbursable_amount',
        help="Total executable amount in the currency of the company, "
             "negative for credit notes.")
    executable_total = fields.Monetary(
        string='Total executable', store=True, readonly=True,
        compute='_compute_executable_amount')
    executable_total_signed = fields.Monetary(
        string='Total executable in Invoice Currency',
        currency_field='currency_id',
        store=True, readonly=True,
        compute='_compute_executable_amount',
        help="Total executable amount in the currency of the invoice, "
             "negative for credit notes.")
    executable_total_company_signed = fields.Monetary(
        string='Total executable in Company Currency',
        currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_executable_amount',
        help="Total executable amount in the currency of the company, "
             "negative for credit notes.")

    @api.multi
    @api.depends('reimbursable_ids')
    def _compute_reimbursable_count(self):
        for rec in self:
            rec.reimbursable_count = len(rec.reimbursable_ids)

    @api.multi
    @api.depends('reimbursable_ids.amount', 'currency_id', 'company_id',
                 'date_invoice', 'type')
    def _compute_reimbursable_amount(self):
        for rec in self:
            rec.reimbursable_total = sum(
                line.amount for line in rec.reimbursable_ids)
            amount = rec.reimbursable_total
            if (
                rec.currency_id and rec.company_id and
                rec.currency_id != rec.company_id.currency_id
            ):
                currency_id = rec.currency_id.with_context(
                    date=rec.date_invoice)
                amount = currency_id.compute(
                    rec.reimbursable_total, rec.company_id.currency_id)
            sign = rec.type in ['in_refund', 'out_refund'] and -1 or 1
            rec.reimbursable_total_company_signed = amount * sign
            rec.reimbursable_total_signed = rec.reimbursable_total * sign

    @api.multi
    @api.depends('reimbursable_total', 'amount_total',
                 'reimbursable_total_signed', 'amount_total_signed',
                 'reimbursable_total_company_signed',
                 'amount_total_company_signed', )
    def _compute_executable_amount(self):
        for rec in self:
            rec.executable_total = rec.reimbursable_total + rec.amount_total
            rec.executable_total_signed = (
                rec.reimbursable_total_signed + rec.amount_total_signed)
            rec.executable_total_company_signed = (
                rec.reimbursable_total_company_signed +
                rec.amount_total_company_signed
            )

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()
        self.reimbursable_ids._onchange_partner_id()
        return res

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        res = super().finalize_invoice_move_lines(move_lines)
        for reimbursable in self.reimbursable_ids.filtered(
            lambda r: r.amount != 0
        ):
            res.append((0, 0, self.line_get_convert(
                reimbursable._invoice_reimbursable_move_line_get(),
                reimbursable.partner_id.id
            )))
        return res

    @api.multi
    def compute_invoice_totals(self, company_currency, invoice_move_lines):
        total, total_currency, iml = super().compute_invoice_totals(
            company_currency, invoice_move_lines)
        price = self.reimbursable_total
        if self.currency_id != company_currency:
            date = self._get_currency_rate_date() or fields.Date.context_today(
                self)
            currency = self.currency_id.with_context(
                date=date)
            if not (self.get('currency_id') and self.get('amount_currency')):
                amount_currency = currency.round(price)
                price = currency.compute(price, company_currency)
        else:
            amount_currency = False
            price = self.currency_id.round(price)
        if self.type in ('out_invoice', 'in_refund'):
            total += price
            total_currency += amount_currency or price
        else:
            total -= price
            total_currency -= amount_currency or price
        return total, total_currency, iml

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None,
                        description=None, journal_id=None):
        values = super()._prepare_refund(
            invoice, date_invoice, date, description, journal_id)
        if invoice.reimbursable_ids:
            values['reimbursable_ids'] = self._refund_cleanup_lines(
                invoice.reimbursable_ids)
        return values


class AccountInvoiceReimbursable(models.Model):
    _name = 'account.invoice.reimbursable'

    invoice_id = fields.Many2one(
        'account.invoice', required=True
    )
    company_id = fields.Many2one(
        'res.company', related='invoice_id.company_id'
    )
    product_id = fields.Many2one(
        "product.product",
        required=False,
        domain="[('type','=','service'), "
               "'|',('company_id', '=', parent.company_id), "
               "('company_id', '=', False)]"
    )
    partner_id = fields.Many2one(
        "res.partner", required=True,
        domain="['|',('company_id', '=', parent.company_id), "
               "('company_id', '=', False)]"
    )
    amount = fields.Monetary(
        currency_field='currency_id', required=True, default=0.,
    )
    name = fields.Text(required=True)
    currency_id = fields.Many2one(
        'res.currency',
        related='invoice_id.currency_id',
    )
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags',
    )
    account_id = fields.Many2one(
        'account.account', string='Account',
        required=True,
        domain=[('deprecated', '=', False)],
    )
    description = fields.Char(readonly=True,
                              store=True, compute='_compute_description')

    @api.depends('name', 'partner_id', 'product_id')
    def _compute_description(self):
        for rec in self:
            rec.description = _('%s from %s') % (
                rec.name, rec.partner_id.display_name)

    @api.multi
    def _invoice_reimbursable_move_line_get(self):
        self.ensure_one()
        return {
            'reimbursable_id': self.id,
            'type': 'reimbursable',
            'partner_id': self.partner_id.id,
            'name': self.name.split('\n')[0][:64],
            'price_unit': self.amount,
            'quantity': 1,
            'price': self.amount,
            'account_id': self.account_id.id,
            'product_id': self.product_id.id,
            'uom_id': self.product_id.uom_id.id,
            'account_analytic_id': self.account_analytic_id.id,
            'invoice_id': self.invoice_id.id,
            'analytic_tag_ids': [(4, analytic_tag.id, None)
                                 for analytic_tag in self.analytic_tag_ids]
        }

    @api.multi
    def set_default_account(self):
        """Hook function that should be upgraded for Customer invoices
        with receivables"""
        if self.partner_id and self.invoice_id.type in (
            'in_invoice', 'in_refund'
        ):
            p = self.partner_id.with_context(
                force_company=self.invoice_id.company_id.id)
            pay_account = p.property_account_payable_id
            return pay_account
        return False

    @api.multi
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            rec.account_id = rec.set_default_account()

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.name = record.product_id.display_name
