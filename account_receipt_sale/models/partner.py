from odoo import models, fields, api


class Partner(models.Model):
    _inherit = "res.partner"
    use_receipts = fields.Boolean(string='Use Receipts')

    @api.onchange('use_receipts')
    def onchange_use_receipts(self):
        if self.use_receipts:
            # Partner is receipts, assign a receipts
            # fiscal position only if there is none
            if not self.property_account_position_id:
                company = self.company_id or self.env.company
                self.property_account_position_id = \
                    self.env['account.fiscal.position'] \
                        .get_receipts_fiscal_pos(company)
        else:
            # Unset the fiscal position only if it was receipts
            if self.property_account_position_id.receipts:
                self.property_account_position_id = False
