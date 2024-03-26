# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _default_sale_create_invoice_policy(self):
        #  In order to avoid errors in the tests CI environment when the tests
        #  Create of Invoice by Sale Order using sale.advance.payment.inv object
        #  is necessary let default policy as sale_order
        #  TODO: Is there other form to avoid this problem?
        result = "stock_picking"
        module_base = self.env["ir.module.module"].search([("name", "=", "base")])
        if module_base.demo:
            result = "sale_order"
        return result

    sale_create_invoice_policy = fields.Selection(
        selection=[
            ("sale_order", "Sale Order"),
            ("stock_picking", "Stock Picking"),
        ],
        string="Sale Create Invoice Policy",
        help="Define, when Product Type are not service, if Invoice"
        " should be create from Sale Order or Stock Picking.",
        default=_default_sale_create_invoice_policy,
    )
