# Copyright 2017-2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def _get_rates(self, company, date):
        """
        Inheritance to use the provided custom rate by user
        instead of the rate from odoo.
        """
        custom_rate = self.env.context.get("custom_rate")
        to_currency = self.env.context.get("to_currency")
        if custom_rate and to_currency:
            return {
                currency.id: custom_rate if currency == to_currency else 1.0
                for currency in self
            }
        return super()._get_rates(company, date)
