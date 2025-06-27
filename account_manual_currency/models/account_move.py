from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    use_manual_rate = fields.Boolean(string="Use Manual Rate")
    manual_currency_rate = fields.Float(string="Manual Currency Rate", digits=(16, 6))

    def _post(self, soft=True):
        # Separate moves that need manual rate
        manual_moves = self.filtered(lambda m: m.use_manual_rate and m.manual_currency_rate)
        normal_moves = self - manual_moves

        posted = self.env['account.move']

        if manual_moves:
            ctx = dict(self.env.context)
            # We assume same company / rate per batch
            ctx.update(
                custom_rate=manual_moves[0].manual_currency_rate,
                to_currency=manual_moves[0].company_id.currency_id,
            )
            posted |= super(AccountMove, manual_moves.with_context(**ctx))._post(soft=soft)

        if normal_moves:
            posted |= super(AccountMove, normal_moves)._post(soft=soft)

        return posted
