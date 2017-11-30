# -*- coding: utf-8 -*-
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    enable_rounding = fields.Boolean(
        string='Enable rounding',
        help='This field enables swedish rounding (if configured) '
             'for supplier invoices'
    )
