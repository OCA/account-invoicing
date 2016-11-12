# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    to_refund_so = fields.Boolean(
        "To Refund in SO",
        help='Trigger a decrease of the delivered quantity in the associated '
             'Sale Order',
    )
