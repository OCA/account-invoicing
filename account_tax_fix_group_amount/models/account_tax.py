#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountTax (models.Model):
    _inherit = 'account.tax'

    amount_type = fields.Selection(
        selection_add=[
            ('last_percent', "Last percentage of group"),
        ],
    )

    def _compute_amount(self, base_amount, price_unit,
                        quantity=1.0, product=None, partner=None):
        self.ensure_one()

        if self._context.get('handle_price_include', True):
            price_include = (self.price_include
                             or self._context.get('force_price_include'))
        else:
            price_include = False

        # last_percent is computed using its siblings in `compute_all``
        if self.amount_type == 'last_percent' and not price_include:
            return 0
        else:
            return super()._compute_amount(
                base_amount, price_unit,
                quantity=quantity, product=product, partner=partner)

    @api.multi
    def _extract_tax_values(self, taxes_dict):
        """
        Helper method to extract values of tax `self`
        from what is returned by `compute_all`.
        """
        self.ensure_one()
        return next(filter(
            lambda t: t['id'] == self.id, taxes_dict['taxes']
        ))

    @api.multi
    def compute_all(self, price_unit,
                    currency=None, quantity=1.0, product=None, partner=None):
        res = super(AccountTax, self).compute_all(
            price_unit,
            currency=currency, quantity=quantity,
            product=product, partner=partner)
        if 'last_percent' in self.mapped('amount_type'):
            self._fix_group_percent_amount(res, currency)
        return res

    @api.multi
    def _fix_group_percent_amount(self, res, currency):
        """
        Compute the amount of 'last_percent' tax.
        """
        parent_tax = self.search([
            ('children_tax_ids', 'in', self.ids),
        ])
        # Detect when children taxes are computed
        # all together in a single `compute_all` call.
        # Note that at this moment we have both the parameter `currency`
        # and the `base_values` in the context.
        if len(parent_tax) == 1 and parent_tax.children_tax_ids == self:
            children_taxes = parent_tax.children_tax_ids.sorted(
                key=lambda r: r.sequence
            )
            sibling_taxes = children_taxes[:-1]
            last_child_tax = children_taxes[-1]
            siblings_percent = set(sibling_taxes.mapped('amount_type')) \
                == {'percent'}
            none_price_include = set(children_taxes.mapped('price_include')) \
                == {False}
            last_child_is_last_percent = \
                last_child_tax.amount_type == 'last_percent'
            if siblings_percent and none_price_include \
               and last_child_is_last_percent:
                last_sibling_amount = self._compute_fixed_last_child_amount(
                    res, currency, sibling_taxes, last_child_tax)
                # Inject the fixed amount in the result dictionary
                sibling_tax_values = last_child_tax._extract_tax_values(res)
                sibling_tax_values['amount'] = last_sibling_amount
        return True

    @api.multi
    def _compute_fixed_last_child_amount(self, res, currency,
                                         sibling_taxes, last_child_tax):
        """
        Correctly compute the amount of the last child tax.

        All taxes are percent taxes and none have tax included price.
        The last child's amount is computed as the difference
        between the amounts of:
         - a hypothetical tax having a percent equal to
           the sum of all its siblings and the last child
         - the sum of all its siblings

        :return: The last child's amount
        """
        siblings_amount = 0
        # Compute amount for all the siblings
        for sibling_tax in sibling_taxes:
            sibling_tax_values = sibling_tax._extract_tax_values(res)
            sibling_tax_amount = sibling_tax_values['amount']
            siblings_amount += sibling_tax_amount
        siblings_amount_round = currency.round(siblings_amount)

        # Compute how much a hypothetical grouped tax amount would be,
        # if it were a percent tax having
        # percentage equal to the sum of all the siblings and the last_child
        group_total_excluded, group_total_included, group_base = \
            self.env.context.get('base_values')
        group_amount_percent_tax = self.new({
            'name': 'Group percent tax',
            'amount_type': 'percent',
            'price_include': False,
            'amount': sum(sibling_taxes.mapped('amount'))
                    + last_child_tax.amount
        })
        group_amount = group_amount_percent_tax._compute_amount(group_base, 1)
        group_amount_round = currency.round(group_amount)

        # The last child's amount is the difference between
        # the hypothetical group tax
        # and the amount of all the siblings' amount
        last_sibling_amount = group_amount_round - siblings_amount_round
        last_sibling_amount_round = currency.round(last_sibling_amount)

        return last_sibling_amount_round
