# Copyright 2022 Darío Cruz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveTag(models.Model):
    _name = "account.move.tag"
    _order = "name"
    _description = "Account Move Tag"

    name = fields.Char(required=True,)
    description = fields.Text(string="Description",)
    color = fields.Integer(string="Color Index",)
    active = fields.Boolean(string="Active", default=True,)
    company_id = fields.Many2one("res.company", string="Company",)
    sequence = fields.Integer(
        default=lambda self: self.env["ir.sequence"].next_by_code("account.move.tag")
        or 0,
        required=True,
    )

    _sql_constraints = [("name_uniq", "unique (name)", "Tag name already exists!")]
