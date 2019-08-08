# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    brand_id = fields.Many2one('res.partner', string='Brand',
                               domain="[('type', '=', 'brand')]")
