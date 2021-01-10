# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_related_invoices(self):
        """Overridden from stock_account to return the customer invoices
        related to this stock move.
        """
        invoices = super()._get_related_invoices()
        line_invoices = self.mapped("sale_line_id.order_id.invoice_ids").filtered(
            lambda x: x.state == "posted"
        )
        invoices |= line_invoices
        return invoices
