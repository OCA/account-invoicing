# Copyright 2017 Eficent Business and IT Consulting Services
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        """Remove lines with qty=0 when making refunds."""
        res = super()._onchange_purchase_auto_complete()
        if self.type == "in_refund":
            self.line_ids -= self.invoice_line_ids.filtered(
                lambda x: float_is_zero(
                    x.quantity, precision_rounding=x.product_uom_id.rounding
                )
            )
        return res
