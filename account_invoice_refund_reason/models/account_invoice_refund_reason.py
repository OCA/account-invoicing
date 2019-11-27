# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceRefundReason(models.Model):
    _name = 'account.invoice.refund.reason'
    _description = 'Account Invoice refund Reasons'

    name = fields.Char('Name', required=True)
