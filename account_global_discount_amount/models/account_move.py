# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = ["account.move", "discount.mixin"]
    _name = "account.move"
    _gd_lines_field = "invoice_line_ids"
    _gd_tax_field = "tax_ids"


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line", "discount.line.mixin"]
    _name = "account.move.line"

    _gd_parent_field = "move_id"
