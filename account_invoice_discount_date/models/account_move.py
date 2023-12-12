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

    @api.depends("line_ids.discount_date")
    def _compute_discount_date(self):
        """Set discount_date to the earliest Discount date of lines with Date maturity"""
        for record in self:
            d_dates = record.line_ids.filtered("date_maturity").mapped("discount_date")
            new_discount_date = d_dates and sorted(d_dates)[0] or None
            if new_discount_date != record.discount_date or not new_discount_date:
                record.discount_date = new_discount_date

    def _inverse_discount_date(self):
        """When set Discount date, update all move lines with Date maturity"""
        for record in self:
            for line in record.line_ids:
                line.discount_date = line.date_maturity and record.discount_date
