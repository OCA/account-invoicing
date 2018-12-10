# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    account_invoice_analytic_line_product_id = fields.Many2one(
        'product.product', string='Invoice product for analytic lines',
        help='This product will be used to invoice analytic lines there is no '
        'explicit product configured on the customer or the project',
    )

    @api.multi
    def set_account_invoice_analytic_line_product_id(self):
        existing = self.env['ir.property'].search(
            self.env['ir.property']._get_domain(
                'account_invoice_analytic_line_product_id', 'res.partner',
            ) + [('res_id', '=', False)],
            limit=1,
            order='company_id',
        )
        if not self.account_invoice_analytic_line_product_id:
            existing.unlink()
            return
        if existing:
            existing.write({
                'value': self.account_invoice_analytic_line_product_id,
            })
            return
        self.env['ir.property'].create({
            'name': 'account_invoice_analytic_line_product_id',
            'fields_id': self.env['ir.model.fields'].search([
                ('model', '=', 'res.partner'),
                ('name', '=', 'account_invoice_analytic_line_product_id'),
            ]).id,
            'value': self.account_invoice_analytic_line_product_id,
        })

    @api.multi
    def get_default_account_invoice_analytic_line_product_id(self, _fields):
        value = self.env['ir.property'].get(
            'account_invoice_analytic_line_product_id', 'res.partner',
        )
        return {
            'account_invoice_analytic_line_product_id': value and value.id,
        }
