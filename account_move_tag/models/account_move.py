from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    tag_ids = fields.Many2many(
        comodel_name="account.move.tag",
        relation="account_move_tag_rel",
        column1="move_id",
        column2="tag_id",
        string="Account Move Tags",
        help="Classify and analyze your account move categories "
        "like bills, payments, deposits, etc.",
    )
