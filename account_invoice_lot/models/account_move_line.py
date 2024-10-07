# Copyright 2023 Groupe Voltaire
# @author Guillaume MASSON <guillaume.masson@groupevoltaire.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Serial Number",
        domain="[('product_id', '=', product_id)]",
    )
