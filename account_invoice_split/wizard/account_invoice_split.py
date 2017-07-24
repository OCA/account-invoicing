# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.float_utils import float_compare

import odoo.addons.decimal_precision as dp

FIELD_MAPPING = [
    ('id', 'origin_invoice_line_id'),
    ('product_id', 'product_id'),
    ('name', 'name'),
    ('quantity', 'total_quantity')]


class AccountInvoiceSplit(models.TransientModel):
    _name = 'account.invoice.split'

    line_ids = fields.One2many(
        comodel_name='account.invoice.split.line', inverse_name='wizard_id',
        string='Invoice lines to Split')

    @api.model
    def _get_invoice_id_from_context(self):
        active_ids = self.env.context.get('active_ids')
        if len(active_ids) != 1:
            raise exceptions.UserError(
                _("You can call this action only for a single invoice."))
        return active_ids[0]

    @api.model
    def _get_invoice_from_context(self):
        invoice_id = self._get_invoice_id_from_context()
        invoice = self.env['account.invoice'].browse(invoice_id)
        self._check_invoice(invoice)
        return invoice

    @api.model
    def _check_invoice(self, invoice):
        if invoice.state != 'draft':
            raise UserError(
                _('Invoice must be draft, not %s') % (invoice.state,))

    @api.model
    def default_get(self, fields_list):
        res = super(AccountInvoiceSplit, self).default_get(fields_list)
        invoice = self._get_invoice_from_context()
        split_lines = []
        for line in invoice.invoice_line_ids:
            current_line_values = {
                'origin_invoice_line_id': line.id,
                'product_id': line.product_id.id,
                'name': line.name,
                'total_quantity': line.quantity,
            }
            split_lines.append((0, 0, current_line_values))
        res['line_ids'] = split_lines
        return res

    @api.model
    def _get_invoice_values(self, invoice):
        """Return default value for copy method.
        Can be override to add some fields"""
        return {'invoice_line_ids': []}

    @api.model
    def _create_invoice(self, invoice_to_split, invoice_lines):
        new_invoice = False
        if invoice_lines:
            default = self._get_invoice_values(invoice_to_split)
            default['invoice_line_ids'] = invoice_lines
            new_invoice = invoice_to_split.copy(default=default)
        if not new_invoice:
            raise exceptions.Warning(
                _("There is nothing to split. Please fill "
                  "the 'quantities to split' column."))
        return new_invoice

    @api.multi
    def _split_invoice(self):
        self.ensure_one()

        invoice_to_split = self._get_invoice_from_context()
        invoice_lines = []
        qty_digit_precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')

        for line in self.line_ids:
            invoice_line = line.origin_invoice_line_id
            qty_is_zero = float_is_zero(
                line.quantity_to_split, precision_digits=qty_digit_precision)
            if not qty_is_zero:
                # I Check if the quantity to split isn't greater then the
                # quantity on the origin line
                qty_is_valid = float_compare(
                    line.quantity_to_split,
                    invoice_line.quantity,
                    precision_digits=qty_digit_precision) <= 0
                if not qty_is_valid:
                    raise UserError(
                        _("Quantity to split is greater than "
                          "available quantity"))
                new_invoice_line = line._create_invoice_line()
                # Change the quantity on the origin invoice line
                invoice_line.quantity -= line.quantity_to_split
                # Unlink origin invoice line if quantity is equal to zero
                if invoice_line.quantity == 0.0:
                    invoice_line.sudo().unlink()
                invoice_lines.append((4, new_invoice_line.id))
        new_invoice = self._create_invoice(invoice_to_split, invoice_lines)
        new_invoice.compute_taxes()
        invoice_to_split.compute_taxes()
        return new_invoice.id

    @api.multi
    def split_invoice(self):
        """Return an action which open a tree with the created invoice and
        the orignal invoice"""
        invoice = self._get_invoice_from_context()
        split_invoice = self._split_invoice()
        action_xml_id = {
            'out_invoice': 'action_invoice_tree1',
            'out_refund': 'action_invoice_tree1',
            'in_invoice': 'action_invoice_tree2',
            'in_refund': 'action_invoice_tree2',
        }[invoice.type]
        action = self.env.ref('account.%s' % action_xml_id).read()[0]
        action.update({
            'domain': [('id', 'in', [invoice.id] + [split_invoice])],
        })
        return action


class AccountInvoiceSplitLine(models.TransientModel):
    _name = 'account.invoice.split.line'

    wizard_id = fields.Many2one(
        comodel_name='account.invoice.split', string='Wizard',
        required=True, ondelete='cascade')
    origin_invoice_line_id = fields.Many2one(
        comodel_name='account.invoice.line', string='Origin Invoice Line',
        required=True, ondelete='cascade')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product')
    name = fields.Text(string='Description')
    total_quantity = fields.Float(
        string='Total Quantity',
        digits=dp.get_precision('Product Unit of Measure'))
    quantity_to_split = fields.Float(
        string='Quantity to split in a new invoice',
        digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    def _create_invoice_line(self):
        self.ensure_one()
        default = self._get_invoice_line_values()
        invoice_line = self.origin_invoice_line_id.copy(default=default)
        return invoice_line

    @api.multi
    def _get_invoice_line_values(self):
        """Return default value for copy method
        Can be override to add some fields"""
        self.ensure_one()
        return {
            'quantity': self.quantity_to_split,
            'invoice_id': False,
        }
