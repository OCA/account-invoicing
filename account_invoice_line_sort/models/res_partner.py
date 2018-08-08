# Copyright 2015 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from . import account_invoice


class res_partner(models.Model):
    _inherit = "res.partner"

    line_order = fields.Selection(account_invoice.AVAILABLE_SORT_OPTIONS,
                                  "Sort Invoice Lines By",
                                  default='sequence')
    line_order_direction = fields.Selection(
        account_invoice.AVAILABLE_ORDER_OPTIONS,
        "Sort Direction",
        default='asc')
