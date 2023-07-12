# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from operator import add

from odoo import api, fields, models

import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    extra_discount_amount = fields.Float(
        compute="_compute_special_fields",
        digits=dp.get_precision("Account"),
        store=True,
    )
    advance_amount = fields.Float(
        compute="_compute_special_fields",
        digits=dp.get_precision("Account"),
        store=True,
    )
    delivery_amount = fields.Float(
        compute="_compute_special_fields",
        digits=dp.get_precision("Account"),
        store=True,
    )
    fees_amount = fields.Float(
        compute="_compute_special_fields",
        digits=dp.get_precision("Account"),
        store=True,
    )

    @api.model
    def _get_special_fields(self):
        return {
            "discount": "extra_discount_amount",
            "advance": "advance_amount",
            "delivery": "delivery_amount",
            "fee": "fees_amount",
        }

    @api.depends(
        "invoice_line_ids.product_id.special_type",
        "invoice_line_ids.price_unit",
        "invoice_line_ids.discount",
        "invoice_line_ids.price_subtotal",
    )
    def _compute_special_fields(self):
        """Compute Discount and Advances amounts (sum of all the products of
        these types)
        You can have several types amounts that are added to the same field
        depending on the grouping in '_get_special_fields' (overriding it)
        function.
        """
        # mapping where keys are product special type and values are the
        # invoice fields
        product_to_fields = self._get_special_fields()
        for invoice in self:
            for special_type, field in product_to_fields.iteritems():
                invoice[field] += reduce(
                    add,
                    [
                        line.price_subtotal
                        for line in invoice.invoice_line_ids
                        if line.product_id
                        and line.product_id.special_type == special_type
                    ],
                    0.0,
                )
