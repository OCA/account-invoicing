# Copyright 2022 Foodles (https://www.foodles.com/)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals["category_ids"] = [
            (
                6,
                0,
                self.partner_invoice_id.commercial_partner_id.accounting_category_ids.ids,
            )
        ]
        return invoice_vals
