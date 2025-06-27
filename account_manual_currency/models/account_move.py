from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # Labels se generan automáticamente; no hace falta string=
    use_manual_rate = fields.Boolean()
    manual_currency_rate = fields.Float(digits=(16, 6))

    # pylint: disable=signature-differs
    def _post(self, soft=True):
        """Publicar el asiento usando la tasa manual cuando proceda."""
        manual_moves = self.filtered(
            lambda m: m.use_manual_rate and m.manual_currency_rate
        )
        normal_moves = self - manual_moves

        posted = self.env["account.move"]

        if manual_moves:
            ctx = dict(
                self.env.context,
                custom_rate=manual_moves[0].manual_currency_rate,
                to_currency=manual_moves[0].company_id.currency_id,
            )
            posted |= super(AccountMove, manual_moves.with_context(**ctx))._post(
                soft=soft
            )

        if normal_moves:
            posted |= super(AccountMove, normal_moves)._post(soft=soft)

        return posted
