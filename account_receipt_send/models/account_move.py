from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_mail_template(self):
        if all(move.move_type in {"out_receipt", "in_receipt"} for move in self):
            return "account_receipt_send.email_template_edi_receipt"
        return super()._get_mail_template()
