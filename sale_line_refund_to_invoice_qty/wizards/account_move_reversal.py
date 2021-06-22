# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    sale_qty_not_to_reinvoice = fields.Boolean(
        string="Not reinvoice refunded quantity",
        help="If marked, the quantities refunded in the credit notes will not "
        "be considered as quantities to be reinvoiced in the related Sales Orders",
    )

    def reverse_moves(self):
        return super(
            AccountMoveReversal,
            self.with_context(sale_qty_not_to_reinvoice=self.sale_qty_not_to_reinvoice),
        ).reverse_moves()
