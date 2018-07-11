# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    pro_forma_sequence = fields.Many2one(
        comodel_name='ir.sequence', string='Pro-forma sequence')
