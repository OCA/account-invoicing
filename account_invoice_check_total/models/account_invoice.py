# Copyright 2016 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_round

GROUP_AICT = 'account_invoice_check_total.group_supplier_inv_check_total'


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    check_total = fields.Monetary(
        string='Verification Total',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False)
    check_total_display_difference = fields.Monetary(
        string='Total Difference',
        compute='_compute_total_display_difference')

    @api.multi
    def _compute_total_display_difference(self):
        for invoice in self:
            invoice.check_total_display_difference = float_round(
                invoice.check_total - invoice.amount_total,
                precision_rounding=invoice.currency_id.rounding
            )

    @api.onchange('check_total', 'amount_total')
    def onchange_check_total(self):
        self.check_total_display_difference = float_round(
            self.check_total - self.amount_total,
            precision_rounding=self.currency_id.rounding
        )

    @api.multi
    def action_move_create(self):
        for inv in self:
            if self.env.user.has_group(GROUP_AICT):
                if inv.type in ('in_invoice', 'in_refund') and \
                        float_compare(
                            inv.check_total,
                            inv.amount_total,
                            precision_rounding=inv.currency_id.rounding
                        ) != 0:
                    raise ValidationError(_(
                        'Please verify the price of the invoice!\n\
                        The total amount (%s) does not match\
                        the Verification Total amount (%s)!\n'
                        'There is a difference of %s') % (
                        inv.amount_total,
                        inv.check_total,
                        inv.check_total_display_difference)
                    )
        return super(AccountInvoice, self).action_move_create()

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None,
                        date=None, description=None, journal_id=None):
        vals = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice, date, description, journal_id)

        if invoice.type in ['in_invoice', 'in_refund']:
            vals['check_total'] = invoice.check_total
        return vals
