# Copyright (C) 2022 ForgeFlow Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountMoveRefundReason(models.Model):
    _inherit = "account.move.refund.reason"

    unlink_so = fields.Boolean(string="Unlink from SO")
