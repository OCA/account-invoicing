# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderType(models.Model):
    _inherit = "sale.order.type"

    whole_delivered_invoiceability = fields.Boolean(
        help="Prevent invoicing until everything has been delivered."
    )
