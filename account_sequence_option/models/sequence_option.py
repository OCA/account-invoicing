# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class BaseSequenceOption(models.Model):
    _inherit = "base.sequence.option"

    model = fields.Selection(
        selection_add=[("account.move", "account.move")],
        ondelete={"account.move": "cascade"},
    )
