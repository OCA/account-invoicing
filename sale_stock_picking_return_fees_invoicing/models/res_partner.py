# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    charge_customer_stock_return = fields.Boolean(
        track_visibility="always",
        help="Tick this box if you wish to charge your customer a fee in "
        "case of return of goods",
        default=False
    )
