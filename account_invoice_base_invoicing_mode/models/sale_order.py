# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoicing_mode = fields.Selection(related="partner_invoice_id.invoicing_mode")
