# -*- coding: utf-8 -*-
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_account(self):
        is_corrispettivo = self._context.get('default_corrispettivo', False)
        res = False
        if is_corrispettivo:
            partner_ids = self.env['res.partner'].search(
                [('corrispettivi', '=', True)])
            if not partner_ids:
                raise UserError(
                    _('No partner "corrispettivi" found'))
            partner = partner_ids[0]
            res = partner.property_account_receivable.id
        return res

    def _get_partner_id(self):
        is_corrispettivo = self._context.get('default_corrispettivo', False)
        res = False
        if is_corrispettivo:
            partner_ids = self.env['res.partner'].search(
                [('corrispettivi', '=', True)])
            if not partner_ids:
                raise UserError(
                    _('No partner "corrispettivi" found'))
            res = partner_ids[0].id
        return res

    # set default option on inherited field
    corrispettivo = fields.Boolean(
        string='Corrispettivo', related="journal_id.corrispettivi",
        readonly=True, store=True)
    account_id = fields.Many2one(default=_get_account)
    partner_id = fields.Many2one(default=_get_partner_id)

    @api.multi
    def onchange_company_id(
        self, company_id, part_id, type, invoice_line, currency_id
    ):
        res = super(AccountInvoice, self).onchange_company_id(
            company_id, part_id, type, invoice_line, currency_id)
        is_corrispettivo = self._context.get('default_corrispettivo', False)
        corr_journal_ids = self.env['account.journal'].search(
            [('corrispettivi', '=', True), ('company_id', '=', company_id)])

        # if it is a "corrispettivo" and the company has at least one
        # journal "corrispettivi"
        if is_corrispettivo and corr_journal_ids:
            res['value']['journal_id'] = corr_journal_ids[0]

        # if the company has at least one journal "corrispettivi" but the
        # invoice it isn't a corrispettivo
        elif corr_journal_ids and corr_journal_ids[0] in \
                res['domain']['journal_id'][0][2]:
            # if invoice's on_change has set journal corrispettivi
            if corr_journal_ids[0] == res['value']['journal_id'] and \
               len(res['domain']['journal_id'][0][2]) > 1:
                for j_id in res['domain']['journal_id'][0][2]:
                    if corr_journal_ids[0] != j_id:
                        res['value']['journal_id'] = j_id
                        break
        return res


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    corrispettivi = fields.Boolean(string='Corrispettivi')


class ResPartner(models.Model):
    _inherit = 'res.partner'
    corrispettivi = fields.Boolean(string='Corrispettivi')
