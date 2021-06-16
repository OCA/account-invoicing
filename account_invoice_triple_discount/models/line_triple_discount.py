# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2021 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class LineTripleDiscount (models.AbstractModel):
    _name = "line.triple_discount.mixin"
    _description = "Add triple discount fields and logic"

    discount = fields.Float()
    discount2 = fields.Float(
        'Discount 2 (%)',
        digits=dp.get_precision('Discount'),
    )
    discount3 = fields.Float(
        'Discount 3 (%)',
        digits=dp.get_precision('Discount'),
    )
    discounting_type = fields.Selection(
        string="Discounting type",
        selection=[
            ('additive', 'Additive'),
            ('multiplicative', 'Multiplicative'),
        ],
        default="multiplicative",
        required=True,
        help="Specifies whether discounts should be additive "
        "or multiplicative.\nAdditive discounts are summed first and "
        "then applied.\nMultiplicative discounts are applied sequentially.\n"
        "Multiplicative discounts are default",
    )

    _sql_constraints = [
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         'Discount 2 must be lower than 100%.'),
        ('discount3_limit', 'CHECK (discount3 <= 100.0)',
         'Discount 3 must be lower than 100%.'),
    ]

    def _get_final_discount(self):
        self.ensure_one()
        if self.discounting_type == "additive":
            return self._additive_discount()
        elif self.discounting_type == "multiplicative":
            return self._multiplicative_discount()

    def _additive_discount(self):
        self.ensure_one()
        discount = sum(
            [getattr(self, x) or 0.0 for x in self._discount_fields()]
        )
        if discount <= 0:
            return 0
        elif discount >= 100:
            return 100
        return discount

    def _multiplicative_discount(self):
        self.ensure_one()
        discounts = [1 - (self[x] or 0.0) / 100
                     for x in self._discount_fields()]
        final_discount = 1
        for discount in discounts:
            final_discount *= discount
        return 100 - final_discount * 100

    def _discount_fields(self):
        return ['discount', 'discount2', 'discount3']

    @api.multi
    def triple_discount_preprocess(self):
        """Save the values of the discounts in a dictionary,
        to be restored in postprocess.
        Resetting discount2 and discount3 to 0.0 avoids issues if
        this method is called multiple times.
        Updating the cache provides consistency through recomputations."""
        prev_values = dict()

        # The newly computed discount might have
        # more digits than allowed from field's precision,
        # so let's increase it just for saving it correctly in cache
        discount_field = self._fields['discount']
        discount_original_digits = discount_field._digits
        discount_field._digits = (16, 10)

        for line in self:
            prev_values[line] = dict(
                discount=line.discount,
                discount2=line.discount2,
                discount3=line.discount3,
            )
            line.update({
                'discount': line._get_final_discount(),
                'discount2': 0.0,
                'discount3': 0.0
            })

        # Restore discount field's precision
        discount_field._digits = discount_original_digits
        return prev_values

    @api.model
    def triple_discount_postprocess(self, prev_values):
        """Restore the discounts of the lines in the dictionary prev_values.
        Updating the cache provides consistency through recomputations."""
        for line, prev_vals_dict in list(prev_values.items()):
            line.update(prev_vals_dict)
