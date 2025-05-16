# Copyright 2020 ACSONE SA/NV
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "triple.discount.mixin"]
