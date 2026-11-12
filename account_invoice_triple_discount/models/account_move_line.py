# Copyright 2020 ACSONE SA/NV
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "triple.discount.mixin"]

    # The definition in account.move.line comes after the mixin's in the MRO,
    # so its digits="Discount" would win and round the combined discount.
    # digits=False keeps every decimal and the existing NUMERIC column.
    discount = fields.Float(digits=False)
