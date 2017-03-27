# -*- coding: utf-8 -*-
# Copyright 2011-2016 Agile Business Group
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class account_invoice(models.Model):
    _inherit = "account.invoice"

    internal_number = fields.Char(states={'draft': [('readonly', False)]})
