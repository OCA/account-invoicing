from odoo import models, api

class ResCurrency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_rates(self, company, date, currency_table=None):
        custom_rate = self.env.context.get('custom_rate')
        to_currency = self.env.context.get('to_currency')
        if custom_rate and to_currency:
            # Call super first to get base rates
            rates = super()._get_rates(company, date, currency_table=currency_table)
            rates[to_currency.id] = custom_rate
            return rates
        return super()._get_rates(company, date, currency_table=currency_table)
