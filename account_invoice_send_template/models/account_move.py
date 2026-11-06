# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_mail_template(self):
        # Use the mail template selected in account_move_send_batch_wizard
        mail_template_id = self.sending_data and self.sending_data.get(
            "mail_template_id", False
        )
        if not mail_template_id:
            return super()._get_mail_template()
        return self.env["mail.template"].browse(mail_template_id)
