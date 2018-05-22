# -*- coding: utf-8 -*-
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# Copyright 2018 Simone Rubino - Agile Business Group
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _default_partner_id(self):
        if not self._context.get('default_corrispettivi', False):
            # If this is not a corrispettivo, do nothing
            return False
        return self.env.ref('base.public_user').partner_id.id

    # set default option on inherited field
    corrispettivo = fields.Boolean(
        string='Corrispettivo', related="journal_id.corrispettivi",
        readonly=True, store=True)
    account_id = fields.Many2one()
    partner_id = fields.Many2one(default=_default_partner_id)

    @api.model
    def _default_journal(self):
        if not self._context.get('default_corrispettivi', False):
            # If this is not a corrispettivo, do nothing
            return super(AccountInvoice, self)._default_journal()
        company_id = self._context.get(
            'company_id', self.env.user.company_id)
        return self.env['account.journal'] \
            .get_corr_journal(company_id)

    @api.onchange('company_id')
    def onchange_company_id_corrispettivi(self):
        if not self._context.get('default_corrispettivi', False):
            # If this is not a corrispettivo, do nothing
            return

        self.set_corr_journal()

    @api.onchange('partner_id')
    def onchange_partner_id_corrispettivi(self):
        if not self.partner_id or not self.partner_id.use_corrispettivi:
            # If partner is not set or its use_corrispettivi flag is disabled,
            # do nothing
            return

        self.set_corr_journal()

    @api.multi
    def set_corr_journal(self):
        for invoice in self:
            invoice.journal_id = self.env['account.journal'] \
                .get_corr_journal(invoice.company_id)


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    corrispettivi = fields.Boolean(string='Corrispettivi')

    @api.model
    def get_corr_journal(self, company_id):
        corr_journal_id = self.search(
            [('type', '=', 'sale'),
             ('corrispettivi', '=', True),
             ('company_id', '=', company_id.id)], limit=1)

        if not corr_journal_id:
            raise UserError(_('No journal found for corrispettivi'))

        return corr_journal_id


class ResPartner(models.Model):
    _inherit = 'res.partner'
    use_corrispettivi = fields.Boolean(string='Use Corrispettivi')
