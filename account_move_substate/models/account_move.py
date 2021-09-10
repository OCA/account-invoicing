# Copyright 2021 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(
        selection_add=[("account.move", "Account Move")],
        ondelete={"account.move": "cascade"},
    )


class AccountMove(models.Model):
    _inherit = ["account.move", "base.substate.mixin"]
    _name = "account.move"
    _state_field = "state"
