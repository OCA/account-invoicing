# -*- coding: utf-8 -*-
# Copyright 2019, Wolfgang Pichler, Callino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    rounding_diff_amount = fields.Float(help="Difference equal or under it will generate rounding writeoff",
                                        default=0.01)
    rounding_diff_account_id = fields.Many2one('account.account',
                                               domain=lambda self: [('reconcile', '=', True),
                                                                    ('deprecated', '=', False)],
                                               string="Intermediary account used for small rounding differences writeoff")
    rounding_diff_journal_id = fields.Many2one('account.journal',
                                               string="Intermediary journal used for small rounding differences writeoff")
