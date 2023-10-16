# Copyright 2023 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    _name = "account.journal"
    _inherit = ["account.journal"]

    refund_code = fields.Char(string="Refund Short Code")
