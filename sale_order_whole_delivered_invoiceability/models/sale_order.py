# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    whole_delivered_invoiceability = fields.Boolean(
        compute="_compute_whole_delivered_invoiceability",
        store=True,
        readonly=False,
    )

    @api.depends("partner_id")
    def _compute_whole_delivered_invoiceability(self):
        for record in self:
            if record.partner_id.whole_delivered_invoiceability:
                record.whole_delivered_invoiceability = True

    @api.depends("whole_delivered_invoiceability")
    def _get_invoice_status(self):
        # Intercept the invoice_status computed method to
        # set it as not invoiceable if the delivered quantity
        # is less than the ordered quantity.
        res = super()._get_invoice_status()
        for order in self.filtered("whole_delivered_invoiceability"):
            uncomplete_lines = order.order_line.filtered(
                lambda line: line.product_id.invoice_policy == "delivery"
                and float_compare(
                    line.product_uom_qty,
                    line.qty_delivered,
                    precision_rounding=line.product_uom.rounding,
                )
                > 0
            )
            if uncomplete_lines:
                order.invoice_status = "no"
        return res
