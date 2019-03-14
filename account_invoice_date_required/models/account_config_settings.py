# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountConfigSettings(models.TransientModel):

    _inherit = 'account.config.settings'

    invoice_date_required = fields.Boolean(
        related='company_id.invoice_date_required',
        string='Invoice Date is Required',
    )
