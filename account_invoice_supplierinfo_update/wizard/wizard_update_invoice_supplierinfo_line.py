# © 2016 Chafique DELLI @ Akretion
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields
import odoo.addons.decimal_precision as dp


class WizardUpdateInvoiceSupplierinfoLine(models.TransientModel):
    _name = 'wizard.update.invoice.supplierinfo.line'
    _description = 'Wizard Line to update supplierinfo'

    _SELECTION_STATE = [
        ('new_supplierinfo', 'New Supplier Info'),
        ('update_supplierinfo', 'Update Supplier Info'),
    ]

    wizard_id = fields.Many2one(
        comodel_name='wizard.update.invoice.supplierinfo', required=True,
        ondelete='cascade')

    product_id = fields.Many2one('product.product', string='Product')

    supplierinfo_id = fields.Many2one(comodel_name='product.supplierinfo')

    current_min_quantity = fields.Float(
        related='supplierinfo_id.min_qty', readonly=True)

    new_min_quantity = fields.Float(
        string='New Min Quantity', required=True)

    current_price = fields.Float(
        related='supplierinfo_id.price',
        digits=dp.get_precision('Product Price'),
        readonly=True)

    new_price = fields.Float(
        string='New Unit Price', digits=dp.get_precision('Product Price'),
        required=True)

    price_variation = fields.Float(
        string='Price Variation (%)', compute='_compute_price_variation',
        digits=dp.get_precision('Discount'))

    state = fields.Selection(selection=_SELECTION_STATE)

    @api.depends('current_price', 'new_price')
    @api.multi
    def _compute_price_variation(self):
        self.write({'price_variation': False})
        for line in self.filtered('current_price'):
            line.price_variation = 100 *\
                (line.new_price - line.current_price) / line.current_price

    # Custom Section
    @api.multi
    def _prepare_supplierinfo(self):
        self.ensure_one()
        return {
            'product_tmpl_id': self.product_id.product_tmpl_id.id,
            'name': self.wizard_id.invoice_id.supplier_partner_id.id,
            'min_qty': 0.0,
            'price': self.new_price,
            'delay': 1,
        }
