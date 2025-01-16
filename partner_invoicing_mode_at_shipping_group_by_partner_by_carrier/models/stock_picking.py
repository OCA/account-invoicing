# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _invoice_at_shipping(self):
        self.ensure_one()
        # As we cannot base the logic on sale_id field (it is set to void in grouping module),
        # and as the invoicing mode and one_invoice_per_shipping are commercial fields
        # (same value for all partner hierarchy), we check if any value is set
        return self.picking_type_code == "outgoing" and (
            any(
                (
                    partner.invoicing_mode == "at_shipping"
                    or partner.one_invoice_per_shipping
                )
                for partner in self.move_ids.sale_line_id.order_id.partner_invoice_id
            )
        )
