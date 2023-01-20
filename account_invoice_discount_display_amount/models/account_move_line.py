# Copyright 2022 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_total = fields.Monetary(compute="_compute_discount_amount", store=True)
    price_total_no_discount = fields.Monetary(
        compute="_compute_discount_amount", string="Total Without Discount", store=True
    )

    @api.depends("discount", "price_total")
    def _compute_discount_amount(self):
        invoice_lines_discount = self.filtered(lambda a: not a.exclude_from_invoice_tab)
        for line in invoice_lines_discount:
            price_total_no_discount = line.price_total
            discount_total = 0
            if line.discount:
                taxes = line.tax_ids.compute_all(
                    line.price_unit,
                    line.move_id.currency_id,
                    line.quantity,
                    product=line.product_id,
                    partner=line.partner_id,
                )
                price_total_no_discount = taxes["total_included"]
                discount_total = price_total_no_discount - line.price_total
            line.update(
                {
                    "discount_total": discount_total,
                    "price_total_no_discount": price_total_no_discount,
                }
            )

        # Lines that are not invoice lines are excluded
        (self - invoice_lines_discount).update(
            {
                "discount_total": 0.0,
                "price_total_no_discount": 0.0,
            }
        )
