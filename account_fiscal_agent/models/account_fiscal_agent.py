# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, _


class account_fiscal_agent_tax(models.Model):
    '''
        This Model is created to store the Agent Taxes
    '''
    _name = 'account.fiscal.agent.tax'
    _rec_name = 'position_id'
    _description = 'Account Fiscal Agent Tax'

    position_id = fields.Many2one('account.fiscal.position', 'Fiscal Position',
                                  required=True, ondelete='cascade')
    tax_src_id = fields.Many2one('account.tax', 'Tax Source', required=True)
    tax_dest_id = fields.Many2one('account.tax', 'Replacement Tax')

    _sql_constraints = [
        ('tax_agent_src_dest_uniq',
         'unique (position_id,tax_src_id,tax_dest_id)',
         _('A tax agent fiscal position could be defined only once \
         time on same taxes.'))
    ]


class account_fiscal_agent_account(models.Model):
    '''
        This Model is created to store the Agent Accounts
    '''
    _name = 'account.fiscal.agent.account'
    _rec_name = 'position_id'
    _description = 'Account Fiscal Agent Account'

    position_id = fields.Many2one('account.fiscal.position', 'Fiscal Position',
                                  required=True, ondelete='cascade')
    account_src_id = fields.Many2one('account.account', 'Account Source',
                                     domain=[('type', '<>', 'view')],
                                     required=True)
    account_dest_id = fields.Many2one('account.account', 'Account Destination',
                                      domain=[('type', '<>', 'view')],
                                      required=True)

    _sql_constraints = [
        ('account_agent_src_dest_uniq',
         'unique (position_id,account_src_id,account_dest_id)',
         _('An agent account fiscal position could be defined only once\
          time on same accounts.'))
    ]


class account_fiscal_agent_journal(models.Model):
    '''
        This Model is created to store the Agent Journals
    '''
    _name = 'account.fiscal.agent.journal'
    _rec_name = 'position_id'
    _description = 'Account Fiscal Agent Journal'

    position_id = fields.Many2one('account.fiscal.position', 'Fiscal Position',
                                  required=True, ondelete='cascade')
    journal_src_id = fields.Many2one('account.journal', 'Journal Source',
                                     required=True)
    journal_dest_id = fields.Many2one('account.journal', 'Journal Destination',
                                      required=True)

    _sql_constraints = [
        ('journal_agent_src_dest_uniq',
         'unique (position_id,journal_src_id,journal_dest_id)',
         _('An agent journal fiscal position could be defined only once\
          time on same accounts.'))
    ]
