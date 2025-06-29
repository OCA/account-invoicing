from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    use_manual_rate = fields.Boolean(string="Use Manual FX Rate")
    manual_currency_rate = fields.Float(
        string="Manual FX Rate", digits=(16, 6)
    )

    # -------------------------------------------------------------------------
    # Posting with manual rate
    # -------------------------------------------------------------------------
    def _post(self, soft=True):
        """
        If the move has ``use_manual_rate`` = True we inject a context
        key 'custom_rate' so that currency conversion uses that value
        instead of the daily rate.
        """
        manual_moves = self.filtered(
            lambda m: m.use_manual_rate and m.manual_currency_rate
        )
        normal_moves = self - manual_moves
        posted = self.env["account.move"]

        if manual_moves:
            ctx = dict(self.env.context)
            ctx.update(
                custom_rate=manual_moves[0].manual_currency_rate,
                to_currency=manual_moves[0].company_id.currency_id,
            )
            posted |= super(
                AccountMove, manual_moves.with_context(**ctx)
            )._post(soft=soft)

        if normal_moves:
            posted |= super(AccountMove, normal_moves)._post(soft=soft)

        return posted
