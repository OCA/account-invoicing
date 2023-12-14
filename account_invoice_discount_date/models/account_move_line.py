# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_date = fields.Date(
        help="Last date at which the discounted amount must be paid in order "
        "for the Early Payment Discount to be granted",
    )
