# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_warn_msg = fields.Text(
        "Invoice Warning",
        help="If set, a warning is shown when creating a customer invoice for"
        " this partner.",
    )
