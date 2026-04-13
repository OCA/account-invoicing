# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):

    _inherit = "account.journal"

    supplier_inv_adjustment_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Supplier Invoice Adjustment Account",
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
    )
