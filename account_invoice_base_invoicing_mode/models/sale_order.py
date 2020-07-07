# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoicing_mode = fields.Selection(related="partner_invoice_id.invoicing_mode")

    # def _create_invoices(self, grouped=False, final=False):
    #     # TODO : Anything specific to do here ? looks like not
    #     res = super()._create_invoices(grouped, final)
    #     return res
