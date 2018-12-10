# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    invoice_discount_id = fields.Many2one(
        'account.invoice.analytic.line.discount',
        ondelete='restrict', string='Discount',
        default=lambda self:
        self.env.ref('account_invoice_analytic_line.discount_none', False),
    )
    invoice_line_id = fields.Many2one(
        'account.invoice.line', ondelete='set null',
    )

    @api.multi
    def _account_invoice_analytic_line(self):
        """Create invoices for lines in self"""
        invoices = self.env['account.invoice']
        for lines in self._account_invoice_analytic_line_group_invoice():
            invoices += self.search(
                lines['__domain']
            )._account_invoice_analytic_line_create_invoice()
        action = self.env['ir.actions.act_window'].for_xml_id(
            'account', 'action_invoice_tree1',
        )
        action['domain'] = [('id', 'in', invoices.ids)]
        return action

    @api.multi
    def _account_invoice_analytic_line_create_invoice(self):
        """Actually create an invoice for lines. We assume they have the same
        partner"""
        if not self:
            return self.env['account.invoice']
        first = self[:1]
        invoice_vals = {
            'partner_id': first.partner_id.id,
            'type': 'out_invoice',
        }
        invoice_vals = self.env['account.invoice'].play_onchanges(
            invoice_vals, ['partner_id'],
        )
        invoice = self.env['account.invoice'].create(invoice_vals)
        for lines in self._account_invoice_analytic_line_group_invoice_lines():
            self.search(
                lines['__domain']
            )._account_invoice_analytic_line_create_invoice_line(invoice)
        invoice.compute_taxes()
        return invoice

    @api.multi
    def _account_invoice_analytic_line_create_invoice_line(self, invoice):
        """Actually create an invoice line from lines in self. We assume they
        have the same product, project and discount"""
        if not self:
            return self.env['account.invoice.line']
        first = self[:1]
        quantity = sum(self.mapped('unit_amount'))
        product = (
            first.product_id or
            first.account_id.account_invoice_analytic_line_product_id or
            invoice.partner_id.account_invoice_analytic_line_product_id
        )
        if not product:
            raise UserError(_(
                'Neither your line, nor the project nor the partner define a '
                'product to use for invoicing, you need to set one of them.'
            ))
        invoice_line_vals = {
            'product_id': product.id,
            'invoice_id': invoice.id,
            'discount': first.invoice_discount_id.discount,
            'quantity': quantity,
            'price_unit': product.with_context(
                pricelist=invoice.partner_id.property_product_pricelist.id,
                partner=invoice.partner_id.id,
                quantity=quantity,
            ).price,
        }
        invoice_line_vals = self.env['account.invoice.line'].play_onchanges(
            invoice_line_vals,
            ['product_id', 'price_unit', 'discount', 'quantity'],
        )
        invoice_line_vals['name'] = first.project_id.name
        invoice_line = self.env['account.invoice.line'].create(
            invoice_line_vals,
        )
        self.write({'invoice_line_id': invoice_line.id})
        return invoice_line

    def _account_invoice_analytic_line_group_invoice_lines(self):
        """Group lines that are supposed to be an invoice line"""
        return self.read_group(
            [('id', 'in', self.ids)],
            ['product_id', 'invoice_discount_id', 'project_id'],
            ['product_id', 'invoice_discount_id', 'project_id'],
            lazy=False,
        )

    def _account_invoice_analytic_line_group_invoice(self):
        """Group lines to invoice"""
        return self.read_group(
            [('id', 'in', self.ids)], ['partner_id'], ['partner_id'],
        )
