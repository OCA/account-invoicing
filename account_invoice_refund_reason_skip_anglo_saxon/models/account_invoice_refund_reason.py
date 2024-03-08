# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountInvoiceRefundReason(models.Model):

    _inherit = "account.move.refund.reason"

    skip_anglo_saxon_entries = fields.Boolean(
        string="Skip anglo saxon entries?",
    )
