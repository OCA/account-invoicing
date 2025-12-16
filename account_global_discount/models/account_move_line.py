# Copyright 2019 Tecnativa - David Vidal
# Copyright 2020-2021 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_global_discount_id = fields.Many2one(
        comodel_name="account.invoice.global.discount",
        string="Invoice Global Discount",
    )
    base_before_global_discounts = fields.Monetary(
        string="Amount Untaxed Before Discounts",
        readonly=True,
    )
