# Copyright 2017-2018 Vauxoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_account_change_currency(self):
        track = self.env['mail.tracking.value']
        today = fields.Date.today()
        for invoice in self.filtered(lambda x: x.state == 'draft'):
            from_currency = invoice.get_last_currency_id()
            if not from_currency or from_currency == invoice.currency_id:
                continue
            ctx = {'company_id': invoice.company_id.id,
                   'date': invoice.date_invoice or today}
            currency = invoice.with_context(**ctx).currency_id
            rate = self.env['res.currency'].with_context(
                **ctx)._get_conversion_rate(
                from_currency, currency, invoice.company_id,
                invoice.date_invoice or today)
            tracking_value_ids = [
                [0, 0, track.create_tracking_values(
                    currency, currency, 'currency_id',
                    self.fields_get(['currency_id'])['currency_id'], 100)],
                [0, 0, track.create_tracking_values(
                    rate, rate, 'rate',
                    currency.fields_get(['rate'])['rate'], 100)],
            ]
            self.message_post(
                subtype='account_invoice_change_currency.mt_currency_update',
                tracking_value_ids=tracking_value_ids)
            for line in invoice.invoice_line_ids:
                line.price_unit *= rate
            for tax in invoice.tax_line_ids:
                tax.amount *= rate

    @api.multi
    def get_last_currency_id(self):
        self.ensure_one()
        last_value = self.env['mail.tracking.value'].sudo().search([
            ('mail_message_id', 'in', self.message_ids.ids),
            ('field', '=', 'currency_id'),
        ], limit=1, order='write_date desc, id desc')
        return self.currency_id.browse(last_value.old_value_integer)
