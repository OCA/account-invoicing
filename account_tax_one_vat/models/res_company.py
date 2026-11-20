# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    account_tax_one_vat = fields.Boolean(
        string="One VAT tax only", help="Avoid the selection of multiple VAT taxes."
    )
