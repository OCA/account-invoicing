# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    sale_qty_to_reinvoice = fields.Boolean(
        string="This credit note will be reinvoiced",
        default="True",
        help="Leave it marked if you will reinvoice the same sale order line "
        "(standard behaviour)",
    )

    def reverse_moves(self):
        sale_qty_to_reinvoice = (
            True if self.refund_method == "modify" else self.sale_qty_to_reinvoice
        )
        return super(
            AccountMoveReversal,
            self.with_context(sale_qty_to_reinvoice=sale_qty_to_reinvoice),
        ).reverse_moves()
