# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    mail_template_id = fields.Many2one(
        comodel_name="mail.template", store=True, readonly=False
    )
