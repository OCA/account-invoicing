# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    tax_calculation_rounding_method = fields.Selection(
        [
            ("round_per_line", "Round per Line"),
            ("round_globally", "Round Globally"),
        ],
        company_dependent=True,
        copy=False,
        help="How total tax amount is computed in sale orders and invoices "
        "when this contact is selected. If no value selected, the method "
        "defined in the company is used.",
    )
