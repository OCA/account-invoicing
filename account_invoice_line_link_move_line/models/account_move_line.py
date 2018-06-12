# -*- coding: utf-8 -*-
# © 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_line_ids = fields.Many2many(
        'account.invoice.line', relation='account_invoice_line_move_line_rel',
        column1='move_line_id', column2='invoice_line_id', auto_join=True,
        string='Invoice lines',
    )
