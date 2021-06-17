# Copyright 2016 Lorenzo Battistini - Agile Business Group
# Copyright 2018 Simone Rubino - Agile Business Group

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _default_partner_id(self):
        if not self._context.get('default_corrispettivi', False):
            # If this is not a receipts (corrispettivi), do nothing
            return False
        return self.env.user.company_id._get_corrispettivi_partner().id

    @api.model
    def _default_journal(self):
        if not self._context.get('default_corrispettivi', False):
            # If this is not a receipts (corrispettivi), do nothing
            return super(AccountInvoice, self)._default_journal()
        company_id = self._context.get(
            'company_id', self.env.user.company_id)
        return self.env['account.journal'] \
            .get_corr_journal(company_id)

    # set default option on inherited field
    corrispettivo = fields.Boolean(
        string='Receipt', related="journal_id.corrispettivi",
        readonly=True, store=True)
    partner_id = fields.Many2one(default=_default_partner_id)
    journal_id = fields.Many2one(default=_default_journal)

    @api.onchange('company_id')
    def onchange_company_id_corrispettivi(self):
        if not self._context.get('default_corrispettivi', False):
            # If this is not a receipts (corrispettivi), do nothing
            return

        self.set_corr_journal()

    @api.onchange('partner_id', 'fiscal_position_id')
    def onchange_partner_id_corrispettivi(self):
        if (
            self.partner_id.use_corrispettivi or
            self.fiscal_position_id.corrispettivi
        ):
            self.set_corr_journal()
        else:
            self.journal_id = self._default_journal()

    @api.multi
    def set_corr_journal(self):
        for invoice in self:
            invoice.journal_id = self.env['account.journal'] \
                .get_corr_journal(invoice.company_id)

    @api.multi
    def corrispettivo_print(self):
        """ Print the receipt and mark it as sent"""
        self.ensure_one()
        self.sent = True
        return self.env.ref('l10n_it_corrispettivi.account_corrispettivi') \
            .report_action(self)


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    corrispettivi = fields.Boolean(string='Receipts')

    @api.model
    def get_corr_journal(self, company_id=None):
        if not company_id:
            company_id = self.env.user.company_id
        corr_journal_id = self.search(
            [('type', '=', 'sale'),
             ('corrispettivi', '=', True),
             ('company_id', '=', company_id.id)], limit=1)

        if not corr_journal_id:
            raise UserError(_('No journal found for receipts'))

        return corr_journal_id


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    corrispettivi = fields.Boolean(string='Receipts')

    @api.model
    def get_corr_fiscal_pos(self, company_id=None):
        if not company_id:
            company_id = self.env.user.company_id
        corr_fiscal_pos = self.search(
            [
                ('company_id', '=', company_id.id),
                ('corrispettivi', '=', True),
            ],
            limit=1
        )
        if not corr_fiscal_pos:
            # Fall back to fiscal positions without company
            corr_fiscal_pos = self.search(
                [
                    ('company_id', '=', False),
                    ('corrispettivi', '=', True),
                ],
                limit=1
            )

        return corr_fiscal_pos


class ResPartner(models.Model):
    _inherit = 'res.partner'

    use_corrispettivi = fields.Boolean(string='Use Receipts')

    @api.onchange('use_corrispettivi')
    def onchange_use_corrispettivi(self):
        if self.use_corrispettivi:
            # Partner is receipts, assign a receipts (corrispettivi)
            # fiscal position only if there is none
            if not self.property_account_position_id:
                company = self.company_id or \
                    self.default_get(['company_id'])['company_id']
                self.property_account_position_id = \
                    self.env['account.fiscal.position'] \
                        .get_corr_fiscal_pos(company)
        else:
            # Unset the fiscal position only if it was receipts (corrispettivi)
            if self.property_account_position_id.corrispettivi:
                self.property_account_position_id = False
