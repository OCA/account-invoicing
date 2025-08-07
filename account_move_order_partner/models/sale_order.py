# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        # Set for use in _get_invoice_grouping_keys
        vals["order_partner_id"] = self.partner_id.id
        return vals

    def _get_invoice_grouping_keys(self):
        keys = super()._get_invoice_grouping_keys()
        if self.env.company.invoice_group_by_order_partner:
            keys.append("order_partner_id")
        return keys
