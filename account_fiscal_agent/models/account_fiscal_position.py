# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class account_fiscal_position(models.Model):
    _inherit = 'account.fiscal.position'

    def map_agent_account(self, account):
        for account_conf in self.fiscal_agent_account_ids:
            if account_conf.account_src_id == account:
                return account_conf.account_dest_id
        raise UserError(
            _("Can't find fiscal agent mapping for account %s") % account.name)

    def map_agent_taxes(self, taxes):
        result = self.env['account.tax'].browse()
        for tax in taxes:
            tax_count = 0
            for t in self.fiscal_agent_tax_ids:
                if t.tax_src_id == tax:
                    tax_count += 1
                    if t.tax_dest_id:
                        result |= t.tax_dest_id
            if not tax_count:
                raise UserError(
                    _("Can't find fiscal agent mapping for tax %s")
                    % tax.name)
        return result

    def map_agent_journal(self, journal):
        for journal_conf in self.fiscal_agent_journal_ids:
            if journal_conf.journal_src_id == journal:
                return journal_conf.journal_dest_id
        raise UserError(
            _("Can't find fiscal agent mapping for journal %s")
            % journal.name)

    with_fiscal_agent = fields.Boolean('With Fiscal Agent?')
    fiscal_agent_company_id = fields.Many2one(
        'res.company', "Fiscal agent company",
        help="Company of the fiscal agent: new invoices will be created for "
             "this company")
    fiscal_agent_account_ids = fields.One2many('account.fiscal.agent.account',
                                               'position_id',
                                               'Fiscal Agent Account')
    fiscal_agent_tax_ids = fields.One2many('account.fiscal.agent.tax',
                                           'position_id',
                                           'Fiscal Agent Tax')
    fiscal_agent_journal_ids = fields.One2many('account.fiscal.agent.journal',
                                               'position_id',
                                               'Fiscal Agent Journal')
