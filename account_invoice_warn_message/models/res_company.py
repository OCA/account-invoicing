# Copyright 2024 Solvos Consultoría Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

INVOICE_WARN_MESSAGE_SELECTION = [
    ("customer", "Customers"),
    ("vendor", "Vendors"),
    ("both", "Both"),
]


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_warn_message_type = fields.Selection(
        INVOICE_WARN_MESSAGE_SELECTION, default=INVOICE_WARN_MESSAGE_SELECTION[0][0]
    )
