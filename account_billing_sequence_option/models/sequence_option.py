# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrSequenceOption(models.Model):
    _inherit = "ir.sequence.option"

    model = fields.Selection(
        selection_add=[("account.billing", "account.billing")],
        ondelete={"account.billing": "cascade"},
    )
