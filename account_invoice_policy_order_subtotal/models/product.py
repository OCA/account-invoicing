# Copyright 2022 Camptocamp SA <telmo.santos@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    invoice_policy = fields.Selection(
        selection_add=[("order_subtotal", "Order subtotal")],
        help="Ordered Quantity: Invoice quantities ordered by the customer.\n"
        "Delivered Quantity: Invoice quantities delivered to the customer.\n"
        "Ordered Subtotal: Invoice subtotal amount ordered by the customer.",
    )

    @api.constrains("invoice_policy")
    def check_invoice_policy(self):
        for product in self:
            if product.invoice_policy == "order_subtotal" and product.type != "consu":
                raise UserError(
                    _(
                        "Order subtotal invoice policy can only be used in products of "
                        "type consumable."
                    )
                )
