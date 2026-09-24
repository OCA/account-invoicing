# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _get_default_mail_subject(self, move, mail_template=None, mail_lang=None):
        partner_subject = move.partner_id.commercial_partner_id.invoice_email_subject
        if partner_subject:
            try:
                subject_rendered = (
                    self.env["mail.template"]
                    .with_context(
                        lang=mail_lang,
                        object=move,
                    )
                    ._render_template(
                        partner_subject,
                        "account.move",
                        [move.id],
                    )
                )
                subject = subject_rendered.get(move.id) or ""
                if subject:
                    return subject
            except Exception as e:
                _logger.warning("Invoice subject render failed: %s", e)

        return super()._get_default_mail_subject(move, mail_template, mail_lang) or ""
