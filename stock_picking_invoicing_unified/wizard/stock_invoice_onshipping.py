# -*- coding: utf-8 -*-
# © 2016 Ainara Galdona <ainaragaldona@avanzosc.es> - Avanzosc S.L.
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from openerp.tools import config


class StockInvoiceOnshipping(models.TransientModel):

    _inherit = 'stock.invoice.onshipping'

    @api.model
    def _default_journal(self, journal_type):
        journals = self.env['account.journal'].search(
            [('type', '=', journal_type)])
        return journals and journals[0] or False

    def _default_sale_journal(self):
        return self._default_journal('sale')

    def _default_sale_refund_journal(self):
        return self._default_journal('sale_refund')

    def _default_purchase_journal(self):
        return self._default_journal('purchase')

    def _default_purchase_refund_journal(self):
        return self._default_journal('purchase_refund')

    journal_id = fields.Many2one(required=False)
    sale_journal = fields.Many2one(
        comodel_name='account.journal', string='Sale Journal',
        domain="[('type', '=', 'sale')]",
        default=_default_sale_journal)
    sale_refund_journal = fields.Many2one(
        comodel_name='account.journal', string='Sale Refund Journal',
        domain="[('type', '=', 'sale_refund')]",
        default=_default_sale_refund_journal)
    purchase_journal = fields.Many2one(
        comodel_name='account.journal', string='Purchase Journal',
        domain="[('type', '=', 'purchase')]",
        default=_default_purchase_journal)
    purchase_refund_journal = fields.Many2one(
        comodel_name='account.journal', string="Purchase Refund Journal",
        domain="[('type', '=', 'purchase_refund')]",
        default=_default_purchase_refund_journal)
    show_sale_journal = fields.Boolean(string="Show Sale Journal")
    show_sale_refund_journal = fields.Boolean(
        string="Show Refund Sale Journal")
    show_purchase_journal = fields.Boolean(string="Show Purchase Journal")
    show_purchase_refund_journal = fields.Boolean(
        string="Show Refund Purchase Journal")

    @api.multi
    @api.onchange('group')
    def onchange_group(self):
        self.ensure_one()
        (sale_pickings, sale_refund_pickings, purchase_pickings,
            purchase_refund_pickings) = self.get_split_pickings()
        self.show_sale_journal = bool(sale_pickings)
        self.show_sale_refund_journal = bool(sale_refund_pickings)
        self.show_purchase_journal = bool(purchase_pickings)
        self.show_purchase_refund_journal = bool(purchase_refund_pickings)

    @api.multi
    def get_partner_sum(self, pickings, partner, inv_type, picking_type,
                        usage):
        move_obj = self.env['stock.move']
        pickings = pickings.filtered(lambda x: x.picking_type_id.code ==
                                     picking_type and x.partner_id == partner)
        if picking_type == 'outgoing':
            moves = pickings.mapped('move_lines').filtered(
                lambda x: x.location_dest_id.usage == usage)
        else:
            moves = pickings.mapped('move_lines').filtered(
                lambda x: x.location_id.usage == usage)
        return (sum([(move_obj._get_price_unit_invoice(m, inv_type) *
                      m.product_uom_qty) for m in moves]),
                moves.mapped('picking_id'))

    @api.multi
    def get_split_pickings_grouped(self, pickings):
        sale_pickings = self.env['stock.picking']
        sale_refund_pickings = self.env['stock.picking']
        purchase_pickings = self.env['stock.picking']
        purchase_refund_pickings = self.env['stock.picking']

        for partner in pickings.mapped('partner_id'):
            so_sum, so_pickings = self.get_partner_sum(
                pickings, partner, 'out_invoice', 'outgoing', 'customer')
            si_sum, si_pickings = self.get_partner_sum(
                pickings, partner, 'out_invoice', 'incoming', 'customer')
            if (so_sum - si_sum) >= 0:
                sale_pickings |= (so_pickings | si_pickings)
            else:
                sale_refund_pickings |= (so_pickings | si_pickings)
            pi_sum, pi_pickings = self.get_partner_sum(
                pickings, partner, 'in_invoice', 'incoming', 'supplier')
            po_sum, po_pickings = self.get_partner_sum(
                pickings, partner, 'in_invoice', 'outgoing', 'supplier')
            if (pi_sum - po_sum) >= 0:
                purchase_pickings |= (pi_pickings | po_pickings)
            else:
                purchase_refund_pickings |= (pi_pickings | po_pickings)
        return (sale_pickings, sale_refund_pickings, purchase_pickings,
                purchase_refund_pickings)

    @api.multi
    def get_split_pickings_nogrouped(self, pickings):
        sale_pickings = pickings.filtered(
            lambda x: x.picking_type_id.code == 'outgoing' and
            x.move_lines[0].location_dest_id.usage == 'customer')
        sale_refund_pickings = pickings.filtered(
            lambda x: x.picking_type_id.code == 'incoming' and
            x.move_lines[0].location_id.usage == 'customer')
        purchase_pickings = pickings.filtered(
            lambda x: x.picking_type_id.code == 'incoming' and
            x.move_lines[0].location_id.usage == 'supplier')
        purchase_refund_pickings = pickings.filtered(
            lambda x: x.picking_type_id.code == 'outgoing' and
            x.move_lines[0].location_dest_id.usage == 'supplier')
        return (sale_pickings, sale_refund_pickings, purchase_pickings,
                purchase_refund_pickings)

    @api.multi
    def get_split_pickings(self):
        picking_obj = self.env['stock.picking']
        pickings = picking_obj.browse(self.env.context.get('active_ids', []))
        if self.group:
            return self.get_split_pickings_grouped(pickings)
        else:
            return self.get_split_pickings_nogrouped(pickings)

    @api.multi
    def create_invoice(self):
        if (config['test_enable'] and
                not self.env.context.get('test_picking_invoicing_unified')):
            return super(StockInvoiceOnshipping, self).create_invoice()
        self.ensure_one()
        res = []
        (sale_pickings, sale_refund_pickings, purchase_pickings,
            purchase_refund_pickings) = self.get_split_pickings()
        if sale_pickings:
            pickings = sale_pickings.with_context(
                date_inv=self.invoice_date, inv_type='out_invoice')
            res += pickings.action_invoice_create(
                journal_id=self.sale_journal.id,
                group=self.group, type='out_invoice')
        if sale_refund_pickings:
            pickings = sale_refund_pickings.with_context(
                date_inv=self.invoice_date, inv_type='out_refund')
            res += pickings.action_invoice_create(
                journal_id=self.sale_refund_journal.id,
                group=self.group, type='out_refund')
        if purchase_pickings:
            pickings = purchase_pickings.with_context(
                date_inv=self.invoice_date, inv_type='in_invoice')
            res += pickings.action_invoice_create(
                journal_id=self.purchase_journal.id,
                group=self.group, type='in_invoice')
        if purchase_refund_pickings:
            pickings = purchase_refund_pickings.with_context(
                date_inv=self.invoice_date, inv_type='in_refund')
            res += pickings.action_invoice_create(
                journal_id=self.purchase_refund_journal.id, group=self.group,
                type='in_refund')
        return res
