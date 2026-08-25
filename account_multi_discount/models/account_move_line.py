# Copyright 2026 Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_distribution = fields.Json(
        copy=True,
        help="Ordered list of percentage discounts applied multiplicatively "
        "to the line.",
    )

    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
        compute="_compute_aggregated_discount",
        inverse="_inverse_discount",
        store=True,
        readonly=False,
        help="Aggregated discount percentage derived multiplicatively from "
        "discount_distribution.",
    )

    @staticmethod
    def _aggregate_discount_distribution(distribution):
        if not distribution:
            return 0.0
        factor = 1.0
        for d in distribution:
            factor *= 1 - (d or 0.0) / 100.0
        return (1 - factor) * 100.0

    @api.depends("discount_distribution")
    def _compute_aggregated_discount(self):
        """Aggregate ``discount_distribution`` multiplicatively into ``discount``."""
        for line in self:
            line.discount = self._aggregate_discount_distribution(
                line.discount_distribution
            )

    def _inverse_discount(self):
        """Reflect a direct ``discount`` write back into the distribution.

        Any direct write on the aggregated ``discount`` always rewrites the
        distribution to a single element (or empties it for a zero discount).
        This keeps the two fields aligned and matches the behaviour of the
        sibling modules ``sale_multi_discount`` and
        ``account_invoice_triple_discount``. The widget remains the way to
        configure a genuine multi-discount setup.
        """
        for line in self:
            line.discount_distribution = [line.discount] if line.discount else []
