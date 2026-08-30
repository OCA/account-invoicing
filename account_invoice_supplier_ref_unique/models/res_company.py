# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    check_invoice_supplier_number = fields.Boolean(
        help="Check this if you want to constraint the unicity for Invoice Supplier"
        " Number",
    )
