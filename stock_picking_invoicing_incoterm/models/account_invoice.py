# -*- coding: utf-8 -*-
# Copyright 2014-2015 Agile Business Group sagl
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    incoterm = fields.Many2one(
        comodel_name='stock.incoterms',
        string='Incoterm',
        help="International Commercial Terms are a series of predefined "
        "commercial terms used in international transactions.",
    )
