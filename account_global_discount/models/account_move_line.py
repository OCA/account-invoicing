# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    global_discount_id = fields.Many2one(
        comodel_name='global.discount',
        string='Global Discount',
        ondelete='restrict',
    )
