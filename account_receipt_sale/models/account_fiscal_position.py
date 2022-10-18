from odoo import models, fields, api


class Position(models.Model):
    _inherit = "account.fiscal.position"
    receipts = fields.Boolean(string='Receipts')

    @api.model
    def get_receipts_fiscal_pos(self, company_id=None):
        if not company_id:
            company_id = self.env.user.company_id
        receipt_fiscal_pos = self.search(
            [
                ('company_id', '=', company_id.id),
                ('receipts', '=', True),
            ],
            limit=1
        )
        if not receipt_fiscal_pos:
            # Fall back to fiscal positions without company
            receipt_fiscal_pos = self.search(
                [
                    ('company_id', '=', False),
                    ('receipts', '=', True),
                ],
                limit=1
            )

        return receipt_fiscal_pos
