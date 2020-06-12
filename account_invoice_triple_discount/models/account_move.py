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
        old_values_by_line_id = {}
        for line in self.line_ids:
            aggregated_discount = line._compute_aggregated_discount(line.discount)
            old_values_by_line_id[line.id] = {
                "price_unit": line.price_unit,
                "discount": line.discount,
            }
            price_unit = line.price_unit * (1 - aggregated_discount / 100)
            line.update({"price_unit": price_unit, "discount": 0})
        res = super(AccountMove, self)._recompute_tax_lines(**kwargs)
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
