# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_mail_template(self):
        # Use the journal mail template if it's common to everyone
        mail_template = fields.first(self).journal_id.mail_template_id
        if not mail_template:
            return super()._get_mail_template()
        if all(mail_template == move.journal_id.mail_template_id for move in self):
            return mail_template
        return super()._get_mail_template()
