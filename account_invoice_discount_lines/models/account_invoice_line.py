# coding: utf-8
# Copyright 2017 Opener B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    discount_real = fields.Float(
        string='Actual Discount (%)', digits=dp.get_precision('Discount'),
        default=0.0)
    discount_display = fields.Float(
        string='Display Discount (%)', digits=dp.get_precision('Discount'),
        compute='_compute_discount_display',
        inverse='_inverse_discount_display')
    discount_line = fields.Boolean(readonly=True)

    @api.multi
    @api.depends('discount', 'discount_real', 'invoice_id.move_id')
    def _compute_discount_display(self):
        for line in self:
            line.discount_display = (
                line.discount_real if line.invoice_id.move_id
                else line.discount)

    @api.multi
    def _inverse_discount_display(self):
        for line in self:
            line.discount = line.discount_display

    @api.multi
    def get_discount_product(self):
        """  API hook """
        self.ensure_one()
        return self.invoice_id.company_id.discount_product
