# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _default_sale_invoicing_policy(self):
        # In order to avoid errors in the CI tests environment when Created
        # Invoice from Sale Order using sale.advance.payment.inv object
        # is necessary let default policy as sale_order
        # TODO: Is there other form to avoid this problem?
        result = "stock_picking"
        module_base = self.env["ir.module.module"].search([("name", "=", "base")])
        if module_base.demo:
            result = "sale_order"
        return result

    sale_invoicing_policy = fields.Selection(
        selection=[
            ("sale_order", "Sale Order"),
            ("stock_picking", "Stock Picking"),
        ],
        help="If set to Sale Order, keep native Odoo behaviour for creation of"
        " invoices from Sale Orders.\n"
        "If set to Stock Picking, disallow creation of Invoices from Sale Orders"
        " for the cases where Product Type are 'Product', in case of 'Service'"
        " still will be possible create from Sale Order.",
        default=_default_sale_invoicing_policy,
    )
