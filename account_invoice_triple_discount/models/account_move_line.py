# Copyright 2020 ACSONE SA/NV
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools
from contextlib import contextmanager

from odoo import api, fields, models
from odoo.tools import float_compare


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    discount2 = fields.Float(
        string="Discount 2 (%)",
        digits="Discount",
    )
    discount3 = fields.Float(
        string="Discount 3 (%)",
        digits="Discount",
    )

    @api.model_create_multi
    def create(self, values_list):
        """
        During the create of move lines, if the system detect that there is a
        difference between the balance and the price subtotal, it will update
        the unit price. When computing those, Odoo base module use a single
        discount on creation. So as there is a difference of the price given
        by the UI and the price computed during create method, the system will
        change the unit price of the invoice line. To avoid that, we update
        the discount field to have the aggregated discount, and we change it
        back after the creation.
        (Similar to _recompute_tax_lines on account.move)
        """
        old_values = []
        dp_discount = self.env["decimal.precision"].precision_get("Discount")
        for values in values_list:
            old_discount = values.get("discount", 0.0)
            new_discount = self._get_aggregated_discount_from_values(values)
            tmp_values = {}
            discount_changed = (
                float_compare(old_discount, new_discount, precision_digits=dp_discount)
                != 0
            )
            if discount_changed:
                values["discount"] = new_discount
                tmp_values["discount"] = old_discount
            old_values.append(tmp_values)
        records = super().create(values_list)
        for index, record in enumerate(records):
            values = old_values[index]
            if values:
                record.write(old_values[index])
        return records

    @contextmanager
    def _aggregated_discount(self):
        """A context manager to temporarily change the discount value on the
        records and restore it after the context is exited. It temporarily
        changes the discount value to the aggregated discount value so that
        methods that depend on the discount value will use the aggregated
        discount value instead of the original one.
        """
        discount_field = self._fields["discount"]
        original_digits = discount_field._digits
        # Change the discount field to have a higher precision to avoid
        # rounding errors when computing the aggregated discount
        discount_field._digits = (16, 16)
        # Protect discount field from triggering recompute of totals
        # and calls to the write method on account.move. This is safe
        # because we are going to restore the original value at the end
        # of the method. This is also required to avoid to trigger the
        # _sync_dynamic_lines and _check_balanced methods on account.move
        # that would lead to errors while computing the triple discount
        # on the invoice lines and raise an exception when the computation is called
        # on account.move.line with a date prior to fiscal year close date.
        with self.env.protecting([discount_field], self):
            old_values = {}
            for line in self:
                old_values[line.id] = line.discount
                aggregated_discount = line._compute_aggregated_discount(line.discount)
                line.update({"discount": aggregated_discount})
            yield
            discount_field._digits = original_digits
            for line in self:
                if line.id not in old_values:
                    continue
                line.with_context(
                    restoring_triple_discount=True,
                ).update({"discount": old_values[line.id]})

    @api.depends(
        "quantity",
        "discount",
        "price_unit",
        "tax_ids",
        "currency_id",
        "discount2",
        "discount3",
    )
    def _compute_totals(self):
        # As the totals are recompute based on the discount field, we need
        # to use the aggregated discount value to compute the totals.
        with self._aggregated_discount():
            res = super()._compute_totals()
        return res

    @api.depends(
        "tax_ids",
        "currency_id",
        "partner_id",
        "analytic_distribution",
        "balance",
        "partner_id",
        "move_id.partner_id",
        "price_unit",
        "discount2",
        "discount3",
    )
    def _compute_all_tax(self):
        # As the taxes are recompute based on the discount field, we need
        # to use the aggregated discount value to compute the taxes.
        with self._aggregated_discount():
            res = super()._compute_all_tax()
        return res

    def _convert_to_tax_base_line_dict(self):
        res = super()._convert_to_tax_base_line_dict()
        res["discount"] = self._compute_aggregated_discount(res["discount"])
        return res

    def _compute_aggregated_discount(self, base_discount):
        self.ensure_one()
        discounts = [base_discount]
        for discount_fname in self._get_multiple_discount_field_names():
            discounts.append(getattr(self, discount_fname, 0.0))
        return self._get_aggregated_multiple_discounts(discounts)

    def _get_aggregated_discount_from_values(self, values):
        discount_fnames = ["discount"]
        discount_fnames.extend(self._get_multiple_discount_field_names())
        discounts = []
        for discount_fname in discount_fnames:
            discounts.append(values.get(discount_fname) or 0.0)
        return self._get_aggregated_multiple_discounts(discounts)

    def _get_aggregated_multiple_discounts(self, discounts):
        discount_values = []
        for discount in discounts:
            discount_values.append(1 - (discount or 0.0) / 100.0)
        aggregated_discount = (
            1 - functools.reduce((lambda x, y: x * y), discount_values)
        ) * 100
        return aggregated_discount

    def _get_multiple_discount_field_names(self):
        return ["discount2", "discount3"]
