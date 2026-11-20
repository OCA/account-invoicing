# Copyright 2022 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    discount_total = fields.Monetary(
        compute="_compute_discount_total",
        currency_field="currency_id",
        store=True,
    )
    price_total_no_discount = fields.Monetary(
        compute="_compute_discount_total",
        string="Total Without Discount",
        currency_field="currency_id",
        store=True,
    )

    @api.depends(
        "invoice_line_ids.discount_total", "invoice_line_ids.price_total_no_discount"
    )
    def _compute_discount_total(self):
        invoices_discount = self.filtered(lambda a: a.is_invoice())

        # Invoices with discount
        for invoice in invoices_discount:
            discount_total = sum(invoice.invoice_line_ids.mapped("discount_total"))
            price_total_no_discount = sum(
                invoice.invoice_line_ids.mapped("price_total_no_discount")
            )
            invoice.update(
                {
                    "discount_total": discount_total,
                    "price_total_no_discount": price_total_no_discount,
                }
            )

        # Account moves that are not invoices are excluded
        (self - invoices_discount).update(
            {
                "discount_total": 0.0,
                "price_total_no_discount": 0.0,
            }
        )
