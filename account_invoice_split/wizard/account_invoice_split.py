# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of account_invoice_split,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     account_invoice_split is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     account_invoice_split is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with account_invoice_split.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp

FIELD_MAPPING = [('id', 'origin_invoice_line_id'),
                 ('product_id', 'product_id'),
                 ('name', 'name'),
                 ('quantity', 'total_quantity')]


class AccountInvoiceSplit(models.TransientModel):
    _name = 'account.invoice.split'

    line_ids = fields.One2many(
        comodel_name='account.invoice.split.line', inverse_name='wizard_id',
        string='Invoice lines to Split')

    @api.model
    def _check_condition(self):
        active_ids = self.env.context.get('active_ids')
        assert len(active_ids) == 1
        invoice = self.env['account.invoice'].browse(active_ids)[0]
        if invoice.state != 'draft':
            raise exceptions.Warning(_('Invoice must be draft not %s') %
                                     (invoice.state,))

    @api.model
    def default_get(self, fields_list):
        self._check_condition()
        res = super(AccountInvoiceSplit, self).default_get(self)
        active_ids = self.env.context.get('active_ids')
        assert len(active_ids) == 1
        invoice = self.env['account.invoice'].browse(active_ids)[0]
        split_lines = []
        for line in invoice.invoice_line:
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
        return {'invoice_line': []}

    @api.model
    def _create_invoice(self, invoice_to_split, invoice_lines):
        new_invoice = False
        if invoice_lines:
            default = self._get_invoice_values(invoice_to_split)
            new_invoice = invoice_to_split.copy(default=default)
            new_invoice.write({'invoice_line': invoice_lines})
        if not new_invoice:
            raise exceptions.Warning(
                 _("""There is nothing to split. Please fill
                      the 'quantities to split' column."""))
        return new_invoice

    @api.multi
    def _split_invoice(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids')
        assert len(active_ids) == 1
        invoice_to_split = self.env['account.invoice'].browse(active_ids)[0]
        invoice_lines = []
        for line in self.line_ids:
            if line.quantity_to_split != 0.0:
                # I Check if the quantity to split isn't greater then the
                # quantity on the origin line
                if line.quantity_to_split > \
                        line.origin_invoice_line_id.quantity:
                    raise exceptions.Warning(
                        _("""Quantity to split is greater
                        than available quantity"""))
                new_invoice_line = line._create_invoice_line()
                # Change the quantity on the origin invoice line
                line.origin_invoice_line_id.quantity -= line.quantity_to_split
                # Unlink origin invoice line if quantity is equal to zero
                if line.origin_invoice_line_id.quantity == 0.0:
                    line.origin_invoice_line_id.unlink()
                invoice_lines.append((4, new_invoice_line.id))
        new_invoice = self._create_invoice(invoice_to_split, invoice_lines)
        return new_invoice.id

    @api.multi
    def split_invoice(self):
        """Return an action which open a tree with the created invoice and
        the orignal invoice"""
        inv_obj = self.env['account.invoice']
        aw_obj = self.env['ir.actions.act_window']
        ids = self.env.context.get('active_ids', [])
        invoices = inv_obj.browse(ids)
        split_invoice = self._split_invoice()
        xid = {
            'out_invoice': 'action_invoice_tree1',
            'out_refund': 'action_invoice_tree3',
            'in_invoice': 'action_invoice_tree2',
            'in_refund': 'action_invoice_tree4',
        }[invoices[0].type]
        action = aw_obj.for_xml_id('account', xid)
        action.update({
            'domain': [('id', 'in', ids + [split_invoice])],
        })
        return action


class AccountInvoiceSplitLine(models.TransientModel):
    _name = 'account.invoice.split.line'

    wizard_id = fields.Many2one(
        comodel_name='account.invoice.split', string='Wizard')
    origin_invoice_line_id = fields.Many2one(
        comodel_name='account.invoice.line', string='Origin Invoice Line')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product')
    name = fields.Text(string='Description')
    total_quantity = fields.Float(
        string='Total Quantity',
        digits=dp.get_precision('Product Unit of Measure'))
    quantity_to_split = fields.Float(
        string='Quantity To split in a new invoice',
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
        return {'quantity': self.quantity_to_split}
