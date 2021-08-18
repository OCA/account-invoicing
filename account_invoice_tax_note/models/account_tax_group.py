# Copyright 2018 ACSONE SA/NV (https://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    report_note = fields.Text(
        translate=True,
        help="Note to insert on Invoice Report if the tax group is used.",
    )
