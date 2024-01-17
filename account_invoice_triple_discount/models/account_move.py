# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class AccountMove(models.Model):

    _inherit = "account.move"

    def _recompute_tax_lines(self, **kwargs):
        """
        As the taxes are recalculated based on a single discount, we need to
        simulate a multiple discount by changing the unit price. Values are
        restored after the original process is done
        """
        old_values_by_line_id = {}
        # To simulate multiple discounts by changing the unit price, we need
        # to increase the precision of the field otherwise the result is
        # inaccurate, misaligning the taxes, we restore the value at the end
        # of the process
        digits = self.line_ids._fields["price_unit"]._digits
        dp_discount = self.env["decimal.precision"].precision_get("Discount")
        self.line_ids._fields["price_unit"]._digits = (16, 16)
        for line in self.line_ids.filtered(
            lambda a: float_compare(a.discount2, 0.0, precision_digits=dp_discount) != 0
            or float_compare(a.discount3, 0.0, precision_digits=dp_discount) != 0
        ):
            aggregated_discount = line._compute_aggregated_discount(line.discount)
            old_values_by_line_id[line.id] = {
                "price_unit": line.price_unit,
                "discount": line.discount,
            }
            price_unit = line.price_unit * (1 - aggregated_discount / 100)
            line.update({"price_unit": price_unit, "discount": 0})
        self.line_ids._fields["price_unit"]._digits = digits
        res = super(AccountMove, self)._recompute_tax_lines(**kwargs)
        for line in self.line_ids.filtered(lambda a: a.id in old_values_by_line_id):
            line.update(old_values_by_line_id[line.id])
        return res

    def _has_discount(self):
        self.ensure_one()
        return any(
            [
                line._compute_aggregated_discount(line.discount) > 0
                for line in self.invoice_line_ids
            ]
        )
