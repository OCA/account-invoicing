# -*- coding: utf-8 -*-
# Copyright 2018 Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError

JOURNAL_TYPE_MAP = {
    ('outgoing', 'customer'): ['sale'],
    ('outgoing', 'supplier'): ['purchase_refund'],
    ('outgoing', 'transit'): ['sale', 'purchase_refund'],
    ('incoming', 'supplier'): ['purchase'],
    ('incoming', 'customer'): ['sale_refund'],
    ('incoming', 'transit'): ['purchase', 'sale_refund'],
}


class StockInvoiceOnshipping(models.TransientModel):

    _name = 'stock.invoice.onshipping'
    _description = 'Stock Invoice Onshipping'

    @api.multi
    def _get_journal(self):
        journal_type = self._get_journal_type()
        journal = self.env['account.journal'].search(
            [('type', '=', journal_type)]
        )
        if journal.id:
            return journal.id
        else:
            return False

    @api.multi
    def _get_journal_type(self):
        picking = self.env['stock.picking'].browse(
            self._context.get('active_id')
        )
        picking_type = picking.picking_type_id.code
        for move in picking.move_lines:
            if picking_type == 'incoming':
                usage = move.location_id.usage
            else:
                usage = move.location_dest_id.usage
            break
        if not picking or not picking.move_lines:
            return 'sale'
        return JOURNAL_TYPE_MAP.get((picking_type, usage), ['sale'])[0]

    journal_id = fields.Many2one(
        'account.journal', 'Destination Journal', required=True,
        default=_get_journal
    )
    journal_type = fields.Selection([
        ('purchase_refund', 'Refund Purchase'),
        ('purchase', 'Create Supplier Invoice'),
        ('sale_refund', 'Refund Sale'),
        ('sale', 'Create Customer Invoice')],
        'Journal Type', readonly=True, default=_get_journal_type
    )
    group = fields.Boolean(
        'Group by partner'
    )
    invoice_date = fields.Date(
        'Invoice Date'
    )

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        for record in self:
            record.journal_type = record.journal_id.type

    @api.model
    def view_init(self, fields):
        res = super(StockInvoiceOnshipping, self).view_init(fields)
        pick_obj = self.env['stock.picking']
        count = 0
        active_ids = self._context.get('active_ids', [])
        for pick in pick_obj.browse(active_ids):
            if pick.invoice_state != '2binvoiced':
                count += 1
        if len(active_ids) == count:
            raise UserError(_('Warning!'), _(
                'None of these picking lists require invoicing.'))
        return res

    @api.multi
    def open_invoice(self):
        invoice_ids = self.create_invoice()

        if not invoice_ids:
            raise UserError(_('No invoice created!'))
        list_invoice_ids = []
        for invoice in invoice_ids:
            list_invoice_ids.append(invoice.id)

        data = self.browse(self._ids[0])

        action_model = False
        action = {}

        journal2type = {
            'sale': 'out_invoice',
            'purchase': 'in_invoice',
            'sale_refund': 'out_refund',
            'purchase_refund': 'in_refund'
        }
        inv_type = journal2type.get(data.journal_type) or 'out_invoice'
        data_pool = self.env['ir.model.data']
        if inv_type == "out_invoice":
            action_id = data_pool.xmlid_to_res_id(
                'account.action_invoice_tree1'
            )
        elif inv_type == "in_invoice":
            action_id = data_pool.xmlid_to_res_id(
                'account.action_invoice_tree2'
            )
        elif inv_type == "out_refund":
            action_id = data_pool.xmlid_to_res_id(
                'account.action_invoice_tree3'
            )
        elif inv_type == "in_refund":
            action_id = data_pool.xmlid_to_res_id(
                'account.action_invoice_tree4'
            )

        if action_id:
            action_pool = self.pool['ir.actions.act_window']
            action_pool_id = self.env['ir.actions.act_window'].browse(action_id)
            action = action_pool.read(action_pool_id)

            action[0]['domain'] = "[('id','in', " + str(list_invoice_ids) + ")]"
            return action[0]
        return True

    @api.multi
    def create_invoice(self):
        journal2type = {
            'sale': 'out_invoice',
            'purchase': 'in_invoice',
            'sale_refund': 'out_refund',
            'purchase_refund': 'in_refund'
        }

        acc_journal = self.env["account.journal"]
        inv_type = journal2type.get(self.journal_type) or 'out_invoice'
        active_ids = self.env.context.get('active_ids', [])

        picking = self.env['stock.picking']
        res = picking.action_invoice_create(
            active_ids=active_ids,
            journal_id=self.journal_id.id,
            group=self.group,
            type=inv_type,
        )
        return res
