# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class UpdateSupplierprice(models.TransientModel):
    _name = 'update.supplierprice'

    wizard_line_ids = fields.One2many(
        'update.supplierprice.line',
        'wizard_id',
        string='Wizard lines')

    @api.multi
    def update_product_supplierprice(self):
        self.ensure_one()
        invoice = self.env['account.invoice'].browse(
            self._context['active_id'])
        invoice.signal_workflow('invoice_open')
        for line in self.wizard_line_ids:
            if not line.suppinfo_id:
                vals = {
                    'name': line.supplier_id.id,
                    'min_qty': 0.0,
                    'delay': 1,
                }
                if line.to_variant:
                    vals.update({
                        'product_id': line.product_id.id,
                    })
                else:
                    vals.update({
                        'product_tmpl_id': line.product_id.product_tmpl_id.id,
                    })
                line.suppinfo_id = self.env['product.supplierinfo'].create(
                    vals)
            pricelist_partnerinfos = self.env['pricelist.partnerinfo'].search([
                ('suppinfo_id', '=', line.suppinfo_id.id),
            ])
            if pricelist_partnerinfos:
                pricelist_partnerinfos[0].write({
                    'min_quantity': 0.0,
                    'price': line.new_price_unit,
                })
            else:
                vals = {
                    'suppinfo_id': line.suppinfo_id.id,
                    'min_quantity': 0.0,
                    'price': line.new_price_unit,
                }
                self.env['pricelist.partnerinfo'].create(vals)

    @api.multi
    def invoice_validate(self):
        invoice = self.env['account.invoice'].browse(
            self._context['active_id'])
        invoice.signal_workflow('invoice_open')


class UpdateSupplierpriceLine(models.TransientModel):
    _name = 'update.supplierprice.line'

    wizard_id = fields.Many2one('update.supplierprice',
                                string='Wizard Reference')
    name = fields.Text(string='Description', required=True)
    new_price_unit = fields.Float(string='New Unit Price',
                                  digits=dp.get_precision('Product Price'))
    current_price_unit = fields.Char(string='Current Unit Price')
    suppinfo_id = fields.Many2one('product.supplierinfo',
                                  string='Partner Information')
    to_variant = fields.Boolean(string='Added to the variant',
                                help="if option is checked then supplier is "
                                     "added to the product variant else "
                                     "supplier is added to the "
                                     "product template")
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    product_id = fields.Many2one('product.product', string='Product')
    product_tmpl_id = fields.Many2one('product.template',
                                      string='Product template')
