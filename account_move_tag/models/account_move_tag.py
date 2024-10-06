from random import randint

from odoo import fields, models


class Tag(models.Model):
    _name = "account.move.tag"
    _description = "Account Move Tag"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char("Tag Name", required=True, translate=True)
    color = fields.Integer(default=_get_default_color)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists!"),
    ]
