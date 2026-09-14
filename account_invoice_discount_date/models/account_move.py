# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    discount_date = fields.Date(
        compute="_compute_discount_date",
        inverse="_inverse_discount_date",
        store=True,
        help="Last date at which the discounted amount must be paid in order "
        "for the Early Payment Discount to be granted",
    )
    discount_amount_currency = fields.Monetary(
        string="Discount amount in Currency",
        compute="_compute_discount_amounts",
        store=True,
        currency_field="currency_id",
        help="Total amount to pay, in invoice currency, if the Early "
        "Payment Discount is applied on all lines that grant one",
    )
    discount_balance = fields.Monetary(
        compute="_compute_discount_amounts",
        store=True,
        currency_field="company_currency_id",
        help="Total amount to pay, in company currency, if the Early "
        "Payment Discount is applied on all lines that grant one",
    )

    @api.depends(
        "currency_id",
        "company_currency_id",
        "line_ids.display_type",
        "line_ids.currency_id",
        "line_ids.company_currency_id",
        "line_ids.discount_amount_currency",
        "line_ids.amount_currency",
        "line_ids.discount_balance",
        "line_ids.balance",
    )
    def _compute_discount_amounts(self):
        """Sum discount-or-plain amounts of payment term lines, only when
        at least one of them grants an Early Payment Discount"""
        for move in self:
            payment_lines = move.line_ids.filtered_domain(
                [("display_type", "=", "payment_term")]
            )
            move_currency = move.currency_id
            move_company_currency = move.company_currency_id
            conversion_date = move.invoice_date or move.date
            if any(
                not line.currency_id.is_zero(line.discount_amount_currency)
                for line in payment_lines
            ):
                discount_amount_currency = 0.0
                discount_balance = 0.0
                for line in payment_lines:
                    line_currency = line.currency_id
                    line_company_currency = line.company_currency_id
                    line_dac = (
                        line.amount_currency
                        if line_currency.is_zero(line.discount_amount_currency)
                        else line.discount_amount_currency
                    )
                    discount_amount_currency += line_currency._convert(
                        line_dac,
                        move_currency,
                        move.company_id,
                        conversion_date,
                        round=False,
                    )
                    line_db = (
                        line.balance
                        if line_company_currency.is_zero(line.discount_balance)
                        else line.discount_balance
                    )
                    discount_balance += line_company_currency._convert(
                        line_db,
                        move_company_currency,
                        move.company_id,
                        conversion_date,
                        round=False,
                    )
                move.discount_amount_currency = discount_amount_currency
                move.discount_balance = discount_balance
            else:
                move.discount_amount_currency = False
                move.discount_balance = False

    @api.depends("line_ids.discount_date")
    def _compute_discount_date(self):
        """Set discount_date to the earliest Discount date
        of lines with Date maturity"""
        for record in self:
            d_dates = record.line_ids.filtered_domain(
                [
                    ("display_type", "=", "payment_term"),
                    ("discount_date", "!=", False),
                ]
            ).mapped("discount_date")
            new_discount_date = d_dates and sorted(d_dates)[0] or None
            if new_discount_date != record.discount_date or not new_discount_date:
                record.discount_date = new_discount_date

    def _inverse_discount_date(self):
        """When set Discount date, update all move lines with Date maturity"""
        discount_date_field = self._fields["discount_date"]
        for record in self:
            for line in record.line_ids.filtered_domain(
                [("display_type", "=", "payment_term")]
            ):
                line.discount_date = record.discount_date
                self.env.add_to_compute(discount_date_field, record)
