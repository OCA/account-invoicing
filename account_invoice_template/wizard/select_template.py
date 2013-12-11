# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class wizard_select_template(orm.TransientModel):

    _name = "wizard.select.invoice.template"
    _columns = {
        'template_id': fields.many2one(
            'account.invoice.template',
            'Invoice Template', required=True),
        'line_ids': fields.one2many(
            'wizard.select.invoice.template.line',
            'template_id', 'Lines'),
        'state': fields.selection([
            ('template_selected', 'Template selected'),
            ], 'State'),
    }

    def load_lines(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids, context=context)[0]
        template_pool = self.pool.get('account.invoice.template')
        wizard_line_pool = self.pool.get('wizard.select.invoice.template.line')
        model_data_obj = self.pool.get('ir.model.data')

        template = template_pool.browse(
            cr, uid, wizard.template_id.id,
            context=context)
        for line in template.template_line_ids:
            if line.type == 'input':
                wizard_line_pool.create(cr, uid, {
                    'template_id': wizard.id,
                    'sequence': line.sequence,
                    'name': line.name,
                    'amount': (
                        line.product_id and line.product_id.list_price or 0.0),
                    'account_id': line.account_id.id,
                    'product_id': line.product_id.id,
                    }, context=context)
        if not wizard.line_ids:
            return self.load_template(cr, uid, ids, context=context)
        wizard.write({'state': 'template_selected'}, context=context)

        view_rec = model_data_obj.get_object_reference(
            cr, uid,
            'account_invoice_template', 'wizard_select_template')
        view_id = view_rec and view_rec[1] or False

        return {
            'view_type': 'form',
            'view_id': [view_id],
            'view_mode': 'form',
            'res_model': 'wizard.select.invoice.template',
            'res_id': wizard.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    def load_template(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        template_obj = self.pool.get('account.invoice.template')
        account_invoice_obj = self.pool.get('account.invoice')
        account_invoice_line_obj = self.pool.get('account.invoice.line')
        mod_obj = self.pool.get('ir.model.data')

        wizard = self.browse(cr, uid, ids, context=context)[0]
        if not template_obj.check_zero_lines(cr, uid, wizard):
            raise orm.except_orm(
                _('Error !'),
                _('At least one amount has to be non-zero!'))
        input_lines = {}
        for template_line in wizard.line_ids:
            input_lines[template_line.sequence] = template_line.amount

        computed_lines = template_obj.compute_lines(
            cr, uid,
            wizard.template_id.id, input_lines)

        inv_values = account_invoice_obj.onchange_partner_id(
            cr, uid, ids, wizard.template_id.type,
            wizard.template_id.partner_id.id)['value']
        inv_values['partner_id'] = wizard.template_id.partner_id.id
        inv_values['account_id'] = wizard.template_id.account_id.id
        inv_values['type'] = wizard.template_id.type
        context['type'] = wizard.template_id.type
        inv_id = account_invoice_obj.create(
            cr, uid, inv_values, context=context)
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
                'invoice_id': inv_id,
                'account_analytic_id': analytic_account_id,
                'account_id': line.account_id.id,
                'invoice_line_tax_id': invoice_line_tax_id,
                'price_unit': computed_lines[line.sequence],
                'product_id': line.product_id.id,
            }
            account_invoice_line_obj.create(cr, uid, val, context=context)

        if wizard.template_id.type in ('out_invoice', 'out_refund'):
            xml_id = 'invoice_form'
        else:
            xml_id = 'invoice_supplier_form'
        resource_id = mod_obj.get_object_reference(
            cr, uid, 'account', xml_id)[1]

        return {
            'domain': "[('id','in', [" + str(inv_id) + "])]",
            'name': 'Invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': inv_id or False,
        }


class wizard_select_template_line(orm.TransientModel):
    _description = 'Template Lines'
    _name = "wizard.select.invoice.template.line"
    _columns = {
        'template_id': fields.many2one(
            'wizard.select.invoice.template', 'Template'),
        'sequence': fields.integer('Number', required=True),
        'name': fields.char('Name', size=64, required=True, readonly=True),
        'account_id': fields.many2one(
            'account.account', 'Account',
            required=True, readonly=True),
        'amount': fields.float('Amount', required=True),
        'product_id': fields.many2one('product.product', 'Product'),
    }
