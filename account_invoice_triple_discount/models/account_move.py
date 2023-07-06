# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):

    _inherit = "account.move"

    def _recompute_tax_lines(self, **kwargs):
        """
        As the taxes are recalculated based on a single discount, we need to
        simulate a multiple discount by changing the unit price. Values are
        restored after the original process is done
        """
        # If another module of this repo inherited this function do not execute
        # following code in order to avoid conflict
        if self.env.context.get("avoid_inherit", False) or not any(
            line._compute_aggregated_discount(line.discount) for line in self.line_ids
        ):
            return super(AccountMove, self)._recompute_tax_lines(**kwargs)
        old_values_by_line_id = {}
        # To simulate multiple discounts by changing the unit price, we need
        # to increase the precision of the field otherwise the result is
        # inaccurate, misaligning the taxes, we restore the value at the end
        # of the process
        digits = self.line_ids._fields["price_unit"]._digits
        self.line_ids._fields["price_unit"]._digits = (16, 16)
        for line in self.line_ids:
            aggregated_discount = line._compute_aggregated_discount(line.discount)
            old_values_by_line_id[line.id] = {
                "price_unit": line.price_unit,
                "discount": line.discount,
            }
            price_unit = line.price_unit * (1 - aggregated_discount / 100)
            line.update({"price_unit": price_unit, "discount": 0})
        self.line_ids._fields["price_unit"]._digits = digits
        res = super(
            AccountMove, self.with_context(avoid_inherit=True)
        )._recompute_tax_lines(**kwargs)
        for line in self.line_ids:
            if line.id not in old_values_by_line_id:
                continue
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
