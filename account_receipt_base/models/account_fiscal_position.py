# Copyright 2023 Simone Rubino - TAKOBI
# Copyright 2026 Francesco Ballerini
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    receipts = fields.Boolean()

    @api.model
    def get_receipts_fiscal_pos(self, company_id=None):
        if not company_id:
            company_id = self.env.company
        return self.search(
            [
                ("company_id", "=", company_id.id),
                ("receipts", "=", True),
            ],
            limit=1,
        )
