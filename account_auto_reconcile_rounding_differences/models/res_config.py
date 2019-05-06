# -*- coding: utf-8 -*-
# Copyright 2019, Wolfgang Pichler, Callino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    rounding_diff_amount = fields.Float(related='company_id.rounding_diff_amount',
                                        help="Difference equal or under it will generate rounding writeoff")
    rounding_diff_account_id = fields.Many2one('account.account',
                                               related='company_id.rounding_diff_account_id',
                                               domain=lambda self: [('reconcile', '=', True)],
                                               help="Intermediary account used for small rounding differences writeoff")
    rounding_diff_journal_id = fields.Many2one('account.journal',
                                               related='company_id.rounding_diff_journal_id',
                                               help="Intermediary journal used for small rounding differences writeoff")
