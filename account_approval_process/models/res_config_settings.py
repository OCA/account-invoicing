# Copyright (C) 2020 - TODAY, Elego Software Solutions GmbH, Berlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_approval_process_ids = fields.One2many(
        related="company_id.account_approval_process_ids",
        context={
            "active_test": False,
        },
    )

    has_invoices_for_reset = fields.Boolean(
        related="company_id.has_invoices_for_reset",
    )

    def action_reset_journal_draft_invoices(self):
        return self.company_id.action_reset_journal_draft_invoices()
