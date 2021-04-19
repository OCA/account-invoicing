# Copyright 2021 FactorLibre - César Castañón <cesar.castanon@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoiceRefundLine(models.TransientModel):
    _name = 'account.invoice.refund.line'

    name = fields.Char(
        string="Name",
    )

    sequence = fields.Integer(
        default=10,
    )

    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Account Invoice',
        readonly=True,
    )

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )

    quantity = fields.Float(
        string="Quantity",
        digits=dp.get_precision('Product Unit of Measure'),
    )

    price_unit = fields.Float(
        string="Price Unit",
        digits=dp.get_precision('Product Unit of Measure'),
    )

    discount = fields.Float(
        string="Discount",
        digits=dp.get_precision('Discount')
    )

    invoice_line_tax_ids = fields.Many2many(
        comodel_name='account.tax',
        string='Invoice Line Tax'
    )

    price_subtotal = fields.Float(
        string="Price Subtotal",
        digits=dp.get_precision('Product Unit of Measure'),
    )

    refund_invoice_id = fields.Many2one(
        comodel_name='account.invoice.refund',
        string='Invoice Refund Reference',
        ondelete='cascade',
        index=True,
    )

    origin_line_id = fields.Many2one(
        comodel_name='account.invoice.line',
        string='Original Invoice Line',
    )
