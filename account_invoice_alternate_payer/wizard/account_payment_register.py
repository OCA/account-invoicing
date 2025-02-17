from odoo import api, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.model
    def _get_line_batch_key(self, line):
        res = super()._get_line_batch_key(line)
        move = line.move_id
        payer_id = move.alternate_payer_id.id or move.commercial_partner_id.id
        if payer_id:
            res["partner_id"] = payer_id
        return res
