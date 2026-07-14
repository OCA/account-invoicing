# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_rate_display_type = fields.Selection(
        [
            ("normal", "Unit per Company Currency"),
            ("inverse_rate", "Company Currency per Unit"),
        ],
        default="normal",
        required=True,
        help=(
            "Select how to display exchange rates on invoices.\n"
            "Example (company currency: JPY; 1 USD = 150 JPY):\n"
            "- Unit per company currency → 0.0066 (USD per JPY)\n"
            "- Company currency per unit → 150 (JPY per USD)"
        ),
    )
