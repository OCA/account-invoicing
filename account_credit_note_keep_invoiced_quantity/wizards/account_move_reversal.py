# Copyright 2022 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    keep_invoiced_quantities = fields.Boolean(
        help=(
            "If you check this box, the related purchase or sales order will "
            "not become eligible for reinvoicing the refunded quantities. "
            "Use this option for price corrections or scrapped items."
        )
    )

    @api.onchange("keep_invoiced_quantities")
    def onchange_keep_invoiced_quantities(self):
        """Prevent invalid combination of settings"""
        if self.refund_method == "modify" and self.keep_invoiced_quantities:
            self.refund_method = "refund"

    @api.onchange("refund_method")
    def onchange_refund_method(self):
        """Prevent invalid combination of settings"""
        if self.refund_method == "modify" and self.keep_invoiced_quantities:
            self.keep_invoiced_quantities = False

    def reverse_moves(self):
        """Propagate context option to avoid inclusion of business fields"""
        if self.keep_invoiced_quantities:
            self = self.with_context(avoid_include_business_fields=True)
        return super().reverse_moves()
