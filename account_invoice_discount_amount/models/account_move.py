# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    discount_amount_currency = fields.Monetary(
        string="Discount amount in Currency",
        compute="_compute_discount_amounts",
        store=True,
        currency_field="currency_id",
        help="Total amount to pay, in invoice currency, if the Early "
        "Payment Discount is applied",
    )
    discount_balance = fields.Monetary(
        compute="_compute_discount_amounts",
        store=True,
        currency_field="company_currency_id",
        help="Total amount to pay, in company currency, if the Early "
        "Payment Discount is applied",
    )

    @api.depends(
        "line_ids.display_type",
        "line_ids.discount_amount_currency",
        "line_ids.discount_balance",
    )
    def _compute_discount_amounts(self):
        """Mirror the discount amounts of the payment term line granting an
        Early Payment Discount. Such a payment term can only have a single
        line, and its amounts are signed (negative on bills and refunds)."""
        for move in self:
            discount_payment_term_line = move.line_ids.filtered_domain(
                [
                    ("display_type", "=", "payment_term"),
                    ("discount_amount_currency", "!=", 0.0),
                ]
            )
            move.discount_amount_currency = (
                discount_payment_term_line.discount_amount_currency
            )
            move.discount_balance = discount_payment_term_line.discount_balance
