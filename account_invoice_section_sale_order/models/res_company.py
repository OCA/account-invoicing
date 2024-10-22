# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_section_name_scheme = fields.Char(
        help="This is the name of the sections on invoices when generated from "
        "sales orders. Keep empty to use default. You can use a python "
        "expression with the 'object' (representing sale order) and 'time'"
        " variables."
    )

    invoice_section_grouping = fields.Selection(
        [
            ("sale_order", "Group by sale Order"),
        ],
        help="Defines object used to group invoice lines",
        default="sale_order",
        required=True,
    )
