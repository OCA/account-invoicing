# Copyright 2026 (APSL - Nagarro) Sara Zambrano
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    activity_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible for emails without attachment",
        help="User who will receive the review activity when an email "
        "arrives on this journal's alias without any PDF/XML attachment. "
        "If left empty, the activity is assigned to whoever processes "
        "the email (usually the technical user of the mail cron).",
    )
