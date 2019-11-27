# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    reason_id = fields.Many2one('account.invoice.refund.reason',
                                string="Reason")
