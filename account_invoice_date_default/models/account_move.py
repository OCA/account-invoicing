# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"
    invoice_date = fields.Date(default=datetime.now())
