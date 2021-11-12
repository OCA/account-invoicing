# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_invoicing_policy = fields.Selection(
        selection=[
            ("sale_order", "Sale Order"),
            ("stock_picking", "Stock Picking"),
        ],
        help="Define, when Product Type are not service, if Invoice"
        " should be created from Sale Order or from Stock Picking.",
        default="stock_picking",
    )
