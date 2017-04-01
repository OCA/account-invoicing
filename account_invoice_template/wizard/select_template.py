# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2017 Aurium Technologies (<http://www.auriumtechnologies.com>)
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import except_orm, Warning


class wizard_select_template(models.TransientModel):

    _name = "wizard.select.invoice.template"

    template_id = fields.Many2one(
        comodel_name='account.invoice.template', string='Invoice Template', required=True)
    line_ids = fields.One2many(
        comodel_name='wizard.select.invoice.template.line', inverse_name='template_id', string='Template Lines')
    state = fields.Selection(
        selection=[('template_selected', 'Template selected')], string='State')

    @api.multi
    def check_zero_lines(self):
        if not self.line_ids:
            return True
        for template_line in self.line_ids:
            if template_line.amount:
                return True
        return False

    @api.multi
    def load_lines(self):

        wizard = self.browse(self.ids)[0]
        template_obj = self.env['account.invoice.template']
        wizard_line_obj = self.env['wizard.select.invoice.template.line']
        template = template_obj.browse(wizard.template_id.id)

        view_rec = self.env.ref(
            'account_invoice_template.wizard_select_template')

        for line in template.template_line_ids:
            if line.type == 'input':
                wizard_line_obj.create(
                    {
                        'template_id': wizard.id,
                        'sequence': line.sequence,
                        'name': line.name,
                        'amount': (line.product_id and line.product_id.list_price or 0.0),
                        'account_id': line.account_id.id,
                        'product_id': line.product_id.id,
                    },
                )

        if not self.line_ids:
            return self.load_template()

        self.write({'state': 'template_selected'})
        view_id = view_rec and view_rec.id or False

        return {
            'view_type': 'form',
            'view_id': [view_id],
            'view_mode': 'form',
            'res_model': 'wizard.select.invoice.template',
            'res_id': wizard.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
        }

    @api.multi
    def load_template(self):

        if self._context is None:
            context = {}

        wizard = self.browse(self.ids)[0]

        template_obj = self.env['account.invoice.template']
        account_invoice_obj = self.env['account.invoice']
        account_invoice_line_obj = self.env['account.invoice.line']

        template = template_obj.browse(wizard.template_id.id)

        # if not template_obj.check_zero_lines():
        #    raise except_orm(
        #        _('Error !'),
        #        _('At least one amount has to be non-zero!')) input_lines = {}

        input_lines = {}
        inv_values = {}

        for template_line in wizard.line_ids:
            input_lines[template_line.sequence] = template_line.amount

        computed_lines = template.compute_lines(input_lines)

        inv_values['partner_id'] = wizard.template_id.partner_id.id
        inv_values['account_id'] = wizard.template_id.account_id.id
        inv_values['type'] = wizard.template_id.invoice_type

        inv_id = account_invoice_obj.create(inv_values)

        #
        # load and populate invoice lines from lines in template
        #
        for line in wizard.template_id.template_line_ids:
            analytic_account_id = False
            if line.analytic_account_id:
                analytic_account_id = line.analytic_account_id.id

            invoice_line_tax_id = []
            if line.invoice_line_tax_id:
                tax_ids = []
                for tax in line.invoice_line_tax_id:
                    tax_ids.append(tax.id)
                invoice_line_tax_id.append((6, 0, tax_ids))

            val = {
                'name': line.name,
                'invoice_id': inv_id.id,
                'account_analytic_id': analytic_account_id,
                'account_id': line.account_id.id,
                'invoice_line_tax_ids': invoice_line_tax_id,
                'price_unit': computed_lines[line.sequence],
                'product_id': line.product_id.id,
            }
            account_invoice_line_obj.create(val)

        inv_id.compute_taxes()

        #
        # load and display created invoice from view
        #

        if wizard.template_id.invoice_type in ('out_invoice', 'out_refund'):
            xml_id = 'account.invoice_form'
        else:
            xml_id = 'account.invoice_supplier_form'

        resource_id = self.env.ref(xml_id).id

        return {
            'domain': "[('id','in', [" + str(inv_id.id) + "])]",
            'name': 'Invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'flags': {'initial_mode': 'edit'},
            'res_id': inv_id.id or False,
        }


class wizard_select_template_line(models.TransientModel):
    _description = 'Template Lines'
    _name = "wizard.select.invoice.template.line"

    template_id = fields.Many2one(
        comodel_name='wizard.select.invoice.template', string='Template')
    sequence = fields.Integer(string='Number', required=True)
    name = fields.Char(string='Name', size=64, required=True, readonly=True)
    account_id = fields.Many2one(
        comodel_name='account.account', string='Account', required=True, readonly=True)
    amount = fields.Float(string='Amount', required=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product')
