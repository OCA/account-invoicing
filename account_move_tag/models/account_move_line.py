from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tag_ids = fields.Many2many(related="move_id.tag_ids")
