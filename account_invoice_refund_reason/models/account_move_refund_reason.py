# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountMoveRefundReason(models.Model):
    _name = "account.move.refund.reason"
    _description = "Account Move Refund Reason"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    description = fields.Char()
