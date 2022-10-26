# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools

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
        """
        As the totals are recalculated based on a single discount, we need to
        simulate a multiple discount by changing the discount value. Values are
        restored after the original process is done
        """
        old_values_by_line_id = {}
        digits = self._fields["discount"]._digits
        self._fields["discount"]._digits = (16, 16)
        for line in self:
            aggregated_discount = line._compute_aggregated_discount(line.discount)
            old_values_by_line_id[line.id] = {"discount": line.discount}
            line.update({"discount": aggregated_discount})
        res = super()._compute_totals()
        self._fields["discount"]._digits = digits
        for line in self:
            if line.id not in old_values_by_line_id:
                continue
            line.update(old_values_by_line_id[line.id])
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
        """
        As the taxes are recalculated based on a single discount, we need to
        simulate a multiple discount by changing discount value. Values are
        restored after the original process is done
        """
        digits = self._fields["discount"]._digits
        self._fields["discount"]._digits = (16, 16)
        old_values_by_line_id = {}
        for line in self:
            aggregated_discount = line._compute_aggregated_discount(line.discount)
            old_values_by_line_id[line.id] = {"discount": line.discount}
            line.update({"discount": aggregated_discount})
        res = super()._compute_all_tax()
        self._fields["discount"]._digits = digits
        for line in self:
            if line.id not in old_values_by_line_id:
                continue
            line.update(old_values_by_line_id[line.id])
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
