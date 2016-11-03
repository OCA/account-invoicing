# -*- coding: utf-8 -*-
# Copyright (C) 2016  KMEE - Hendrix Costa
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_ids = fields.Many2many(
        string=u'Sale Orders',
        comodel_name='sale.order',
        compute="_compute_sale_ids"
    )
    sale_order_count = fields.Integer(string='# Sales',
                                      compute='_compute_sale_ids',
                                      readonly=True)

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_sale_ids(self):
        for invoice in self:
            invoice.sale_ids = invoice.mapped(
                'invoice_line_ids.sale_line_ids.order_id')
            invoice.sale_order_count = len(invoice.sale_ids)

    @api.multi
    def action_view_sales(self):
        self.ensure_one()
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders')
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'],
                      [False, 'graph'], [False, 'kanban'], [False, 'calendar'],
                      [False, 'pivot']],
            'target': action.target,
            'res_model': action.res_model,
        }

        if self.sale_order_count == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = self.sale_ids[0].id
        elif self.sale_order_count > 1:
            result['domain'] = "[('id','in',%s)]" % self.sale_ids.mapped('id')
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result
