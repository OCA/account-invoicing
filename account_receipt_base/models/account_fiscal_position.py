#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    receipts = fields.Boolean()

    @api.model
    def get_receipts_fiscal_pos(self, company_id=None):
        if not company_id:
            company_id = self.env.user.company_id
        receipt_fiscal_pos = self.search(
            [
                ("company_id", "=", company_id.id),
                ("receipts", "=", True),
            ],
            limit=1,
        )
        if not receipt_fiscal_pos:
            # Fall back to fiscal positions without company
            receipt_fiscal_pos = self.search(
                [
                    ("company_id", "=", False),
                    ("receipts", "=", True),
                ],
                limit=1,
            )

        return receipt_fiscal_pos
