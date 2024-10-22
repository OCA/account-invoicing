# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from itertools import product

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    extra_discount_amount = fields.Float(
        compute="_compute_special_fields",
        digits="Account",
        store=True,
    )
    advance_amount = fields.Float(
        compute="_compute_special_fields",
        digits="Account",
        store=True,
    )
    delivery_amount = fields.Float(
        compute="_compute_special_fields",
        digits="Account",
        store=True,
    )
    fees_amount = fields.Float(
        compute="_compute_special_fields",
        digits="Account",
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
        product_to_fields = self._get_special_fields()
        fields_name = set(product_to_fields.values())
        # Init to 0
        self.update({f: 0 for f in fields_name})
        for invoice, (special_type, field_name) in product(
            self, product_to_fields.items()
        ):
            invoice[field_name] += sum(
                line.price_subtotal
                for line in invoice.invoice_line_ids
                if line.product_id.special_type == special_type
            )
