# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sale_qty_to_reinvoice = fields.Boolean(
        default=lambda self: self.env.company.reinvoice_credit_note_default,
        help="Leave it marked if you will reinvoice the same sale order line",
        copy=False,
    )
