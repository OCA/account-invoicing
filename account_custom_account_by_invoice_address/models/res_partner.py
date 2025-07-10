# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    use_invoice_address_accounts = fields.Boolean(
        string="Use Custom Accounts per Invoicing Address",
        help="If enabled, the receivable/payable accounts defined on invoice addresses "
        "will be used instead of the commercial entity.",
    )
    parent_use_invoice_address_accounts = fields.Boolean(
        related="parent_id.use_invoice_address_accounts",
        string="Use Custom Accounts",
    )
