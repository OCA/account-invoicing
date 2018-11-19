# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountReinvoiceOtherPartner(models.TransientModel):
    _name = 'account.reinvoice.other.partner'
    _description = 'Reinvoice to another Partner'

    old_partner_id = fields.Many2one('res.partner',
                                     string='Old customer')
    new_partner_id = fields.Many2one('res.partner',
                                     required=True,
                                     string='New customer')
    account_id = fields.Many2one('account.account',
                                 readonly=True,
                                 )
    company_id = fields.Many2one('res.company',
                                 readonly=True,
                                 )
    invoice_journal_id = fields.Many2one('account.journal',
                                         readonly=True,
                                         )
    reinvoice_journal_id = fields.Many2one('account.journal',
                                           required=True,
                                           )
    single_invoice = fields.Boolean('Create a single invoice',
                                    )
    invoice_date = fields.Date('Invoice Date',
                               default=fields.Date.today(),
                               )
    currency_id = fields.Many2one('res.currency',
                                  readonly=True,
                                  )

    @api.model
    def _check_same_company(self, invoices):
        if len(invoices.mapped('company_id')) > 1:
            raise ValidationError(_(
                'All invoices must belong to the same company.'))

    @api.model
    def _check_same_partner(self, invoices):
        if len(invoices.mapped('partner_id')) > 1:
            raise ValidationError(_(
                'All invoices must belong to the same partner.'))

    @api.model
    def _check_same_account(self, invoices):
        if len(invoices.mapped('account_id')) > 1:
            raise ValidationError(_(
                'All invoices must have the same account.'))

    @api.model
    def _check_same_currency(self, invoices):
        if len(invoices.mapped('currency_id')) > 1:
            raise ValidationError(_(
                'All invoices must have the same currency.'))

    @api.model
    def _check_status(self, invoices):
        for state in invoices.mapped('state'):
            if state not in ['open', 'paid']:
                raise ValidationError(_(
                    'All invoices must be in Open or Paid status.'))

    @api.model
    def _check_existing_refunds(self, invoices):
        if invoices.mapped('refund_invoice_ids'):
            raise ValidationError(_(
                'You cannot perform this process for invoices for which '
                'you have already applied a refund.'))

    @api.model
    def _check_invoice_type(self, invoices):
        invoice_types = list(set(invoices.mapped('type')))
        for invoice_type in invoice_types:
            if invoice_type not in ['out_invoice', 'out_refund']:
                raise ValidationError(_(
                    'All invoices must be Customer Invoices or '
                    'Customer Refunds.'))

    @api.model
    def default_get(self, field_list):
        res = super(AccountReinvoiceOtherPartner, self).default_get(field_list)
        invoice_ids = self.env.context['active_ids'] or []
        active_model = self.env.context['active_model']

        if not invoice_ids:
            return res
        invoices = self.env['account.invoice'].browse(invoice_ids)
        self._check_same_company(invoices)
        self._check_same_partner(invoices)
        self._check_same_account(invoices)
        self._check_same_currency(invoices)
        self._check_status(invoices)
        self._check_invoice_type(invoices)
        res['account_id'] = invoices[0].account_id.id
        res['company_id'] = invoices[0].company_id.id
        res['old_partner_id'] = invoices[0].partner_id.id
        res['invoice_journal_id'] = invoices[0].journal_id.id
        res['reinvoice_journal_id'] = invoices[0].company_id.\
            reinvoice_journal_id.id
        res['currency_id'] = invoices[0].currency_id.id
        assert active_model == 'account.invoice', 'Bad context propagation'
        return res

    @api.model
    def _postprocess_new_invoices(self, invoices):
        """ We can potentially merge invoices"""
        return invoices

    @api.model
    def _prepare_credit_aml(self, amount, amount_currency):
        return {
            'name': '',
            'account_id': self.account_id.id,
            'partner_id': amount < 0 and self.new_partner_id.id or
            self.old_partner_id.id,
            'debit': 0.0,
            'credit': abs(amount),
            'amount_currency': amount_currency != 0.0 and
            -1 * abs(amount_currency) or 0.0,
            'currency_id': self.currency_id.id,
        }

    def _prepare_debit_aml(self, amount, amount_currency):
        return {
            'name': '',
            'account_id': self.account_id.id,
            'partner_id': amount < 0 and self.old_partner_id.id or
            self.new_partner_id.id,
            'debit': abs(amount),
            'credit': 0.0,
            'amount_currency': amount_currency != 0.0 and
            abs(amount_currency) or 0.0,
            'currency_id': self.currency_id.id,
        }

    @api.model
    def _prepare_account_move(self, amount, amount_currency):
        aml_credit_data = self._prepare_credit_aml(amount, amount_currency)
        aml_debit_data = self._prepare_debit_aml(amount, amount_currency)

        return {
            'journal_id': self.reinvoice_journal_id.id,
            'date': self.invoice_date,
            'ref': _('Reconciliation of credit reinvoiced to another '
                     'customer'),
            'company_id': self.account_id.company_id.id,
            'line_ids': [(0, 0, aml_debit_data),
                         (0, 0, aml_credit_data)]
        }

    @api.multi
    def process(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        invoices = self.env['account.invoice'].browse(active_ids)
        invoices_new_partner = self.env['account.invoice']
        reversals_old_partner = self.env['account.invoice']
        # Credit all invoices that are open
        for invoice in invoices:
            values = self.env['account.invoice']._prepare_refund(
                invoice, date_invoice=self.invoice_date,
                date=self.invoice_date,
                description=_('Credit to re-invoice to another customer'),
                journal_id=invoice.journal_id.id,
            )
            invoice_refund = self.env['account.invoice'].create(values)
            invoice_refund.action_invoice_open()
            reversals_old_partner += invoice_refund
        if self.single_invoice:
            invoice_new_partner = self.env['account.invoice'].new({
                'partner_id': self.new_partner_id.id,
                'company_id': self.company_id.id,
                'journal_id': self.invoice_journal_id.id,
                'date_invoice': self.invoice_date,
                'type': 'out_invoice',
                'currency_id': self.currency_id.id,
            })
            invoice_new_partner._onchange_partner_id()
            vals = invoice_new_partner._convert_to_write(
                invoice_new_partner._cache)
            invoice_new_partner = self.env['account.invoice'].create(vals)
            for il in invoices.mapped('invoice_line_ids'):
                default_data = {
                    'invoice_id': invoice_new_partner.id,
                }
                if il.invoice_id.type == 'out_refund':
                    default_data['quantity'] = -1*il.quantity
                il.copy(default=default_data)
            if invoice_new_partner.amount_total_company_signed < 0.0:
                for il in invoice_new_partner.invoice_line_ids:
                    il.quantity *= -1
                invoice_new_partner.type = 'out_refund'
            invoices_new_partner += invoice_new_partner
        else:
            for invoice in invoices:
                # Now we create the new invoice
                default_data = {
                    'partner_id': self.new_partner_id.id,
                    'date_invoice': self.invoice_date,
                }
                new_invoice = invoice.copy(default=default_data)
                invoices_new_partner += new_invoice
        # Try to match the new credits to invoices for the old partner as
        # much as possible.
        amls_invoices = invoices.mapped('move_id.line_ids').filtered(
            lambda l: l.partner_id == self.old_partner_id and
            l.account_id == self.account_id and not l.reconciled)
        amls_credits = reversals_old_partner.mapped(
            'move_id.line_ids').filtered(
            lambda l: l.partner_id == self.old_partner_id and
            l.account_id == self.account_id and not l.reconciled)
        self.env['account.move.line'].process_reconciliations(
            [{'mv_line_ids': amls_invoices.ids + amls_credits.ids,
              'type': 'partner',
              'id': self.old_partner_id.id,
              'new_mv_line_dicts': []}])
        new_invoices = self._postprocess_new_invoices(invoices_new_partner)
        new_invoices.action_invoice_open()
        # Now we need to reconcile any open amounts in the credit memos
        # with the invoices with the new customer.
        credit_residual = sum(amls_credits.mapped('amount_residual'))
        credit_residual_currency = sum(amls_credits.mapped(
            'amount_residual_currency'))
        if credit_residual:
            am_data = self._prepare_account_move(credit_residual,
                                                 credit_residual_currency)
            account_move = self.env['account.move'].create(am_data)
            account_move.post()
            # Process reconciliations for the old partner
            old_partner_amls = account_move.line_ids.filtered(
                lambda l: l.partner_id == self.old_partner_id and
                l.account_id == self.account_id and not l.reconciled)
            amls_credits = reversals_old_partner.mapped(
                'move_id.line_ids').filtered(
                lambda l: l.partner_id == self.old_partner_id and
                l.account_id == self.account_id and not l.reconciled)
            self.env['account.move.line'].process_reconciliations(
                [{'mv_line_ids': old_partner_amls.ids + amls_credits.ids,
                  'type': 'partner',
                  'id': self.old_partner_id.id,
                  'new_mv_line_dicts': []}])
            # Process reconciliations for the new partner
            new_partner_amls = account_move.line_ids.filtered(
                lambda l: l.partner_id == self.new_partner_id and
                l.account_id == self.account_id)
            new_invoices_amls = new_invoices.mapped(
                'move_id.line_ids').filtered(
                lambda l: l.partner_id == self.new_partner_id and
                l.account_id == self.account_id)
            self.env['account.move.line'].process_reconciliations(
                [{'mv_line_ids': new_partner_amls.ids + new_invoices_amls.ids,
                  'type': 'partner',
                  'id': self.new_partner_id.id,
                  'new_mv_line_dicts': []}])
