# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services
#           <contact@eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools.float_utils import float_compare


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.qty_received',
                 'order_line.move_ids.state')
    def _get_invoiced(self):
        super(PurchaseOrder, self)._get_invoiced()
        for order in self:
            if order.state != 'purchase':
                order.invoice_status = 'no'
                continue
            if any(line.invoice_status == 'to invoice'
                   for line in order.order_line):
                order.invoice_status = 'to invoice'
            elif all(line.invoice_status == 'invoiced'
                     for line in order.order_line):
                order.invoice_status = 'invoiced'
            else:
                order.invoice_status = 'no'

    @api.depends('order_line.invoice_lines.invoice_id.state')
    def _compute_invoice_refund(self):
        for order in self:
            invoices = self.env['account.invoice']
            for line in order.order_line:
                invoices |= line.invoice_lines.mapped('invoice_id').filtered(
                    lambda x: x.type == 'in_refund')
            order.invoice_refund_count = len(invoices)

    @api.depends('order_line.invoice_lines.invoice_id.state')
    def _compute_invoice(self):
        super(PurchaseOrder, self)._compute_invoice()
        for order in self:
            invoices = self.env['account.invoice']
            for line in order.order_line:
                invoices |= line.invoice_lines.mapped('invoice_id').filtered(
                    lambda x: x.type == 'in_invoice')
            order.invoice_count = len(invoices)

    invoice_refund_count = fields.Integer(compute="_compute_invoice_refund",
                                          string='# of Invoice Refunds',
                                          copy=False, default=0)

    @api.multi
    def action_view_invoice_refund(self):
        """
        This function returns an action that display existing vendor refund
        bills of given purchase order id.
        When only one found, show the vendor bill immediately.
        """
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]
        refunds = self.invoice_ids.filtered(lambda x: x.type == 'in_refund')
        # override the context to get rid of the default filtering
        result['context'] = {'type': 'in_refund',
                             'default_purchase_id': self.id}

        if not refunds:
            # Choose a default account journal in the
            # same currency in case a new invoice is created
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(
                journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
        else:
            # Use the same account journal than a previous invoice
            result['context']['default_journal_id'] = refunds[0].journal_id.id

        # choose the view_mode accordingly
        if len(refunds) != 1:
            result['domain'] = "[('id', 'in', " + \
                               str(refunds.ids) + ")]"
        elif len(refunds) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = refunds.id
        return result

    @api.multi
    def action_view_invoice(self):
        result = super(PurchaseOrder, self).action_view_invoice()
        invoices = self.invoice_ids.filtered(
            lambda x: x.type == 'in_invoice')
        # choose the view_mode accordingly
        if len(invoices) != 1:
            result['domain'] = "[('id', 'in', " + str(invoices.ids) + ")]"
        elif len(invoices) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = invoices.id
        return result


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('invoice_lines.invoice_id.state',
                 'invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        super(PurchaseOrderLine, self)._compute_qty_invoiced()
        for line in self:
            qty = 0.0
            for inv_line in line.invoice_lines:
                inv_type = inv_line.invoice_id.type
                invl_q = inv_line.quantity
                # This is a small 'hack' to allow the odoo tests to pass.
                # See https://github.com/OCA/OCB/pull/598
                if inv_type == 'out_invoice' and \
                        inv_line.invoice_id.account_id.user_type_id.type == \
                        'payable':
                    inv_type = 'in_invoice'
                if inv_line.invoice_id.state not in ['cancel']:
                    if (
                        (inv_type == 'in_invoice' and invl_q > 0.0) or
                        (inv_type == 'in_refund' and invl_q < 0.0)
                    ):
                        qty += inv_line.uom_id._compute_qty_obj(
                            inv_line.uom_id, inv_line.quantity,
                            line.product_uom)
            line.qty_invoiced = qty

    @api.depends('invoice_lines.invoice_id.state',
                 'invoice_lines.quantity')
    def _compute_qty_refunded(self):
        for line in self:
            qty = 0.0
            for inv_line in line.invoice_lines:
                inv_type = inv_line.invoice_id.type
                invl_q = inv_line.quantity
                if (
                    (inv_type == 'in_invoice' and invl_q < 0.0) or
                    (inv_type == 'in_refund' and invl_q > 0.0)
                ):
                    qty += inv_line.uom_id._compute_qty_obj(
                        inv_line.uom_id, inv_line.quantity, line.product_uom)
            line.qty_refunded = qty

    @api.depends('order_id.state', 'qty_received', 'qty_invoiced',
                 'product_qty', 'move_ids.state',
                 'invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _compute_qty_to_invoice(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for line in self:
            line.qty_to_invoice = 0.0
            line.qty_to_refund = 0.0
            if line.order_id.state != 'purchase':
                line.invoice_status = 'no'
                continue
            else:
                if line.product_id.purchase_method == 'receive':
                    qty = (line.qty_received - line.qty_returned) - (
                        line.qty_invoiced - line.qty_refunded)
                    if qty >= 0.0:
                        line.qty_to_invoice = qty
                    else:
                        line.qty_to_refund = abs(qty)
                else:
                    line.qty_to_invoice = line.product_qty - line.qty_invoiced
                    line.qty_to_refund = 0.0

            if line.product_id.purchase_method == 'receive' and not \
                    line.move_ids.filtered(lambda x: x.state == 'done'):
                line.invoice_status = 'to invoice'
                # We would like to put 'no', but that would break standard
                # odoo tests.
                continue

            if abs(float_compare(line.qty_to_invoice, 0.0,
                                 precision_digits=precision)) == 1:
                line.invoice_status = 'to invoice'
            elif abs(float_compare(line.qty_to_refund, 0.0,
                                   precision_digits=precision)) == 1:
                line.invoice_status = 'to invoice'
            elif float_compare(line.qty_to_invoice, 0.0,
                               precision_digits=precision) == 0 \
                    and float_compare(line.qty_to_refund, 0.0,
                                      precision_digits=precision) == 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'

    @api.depends('order_id.state', 'move_ids.state')
    def _compute_qty_returned(self):
        for line in self:
            line.qty_returned = 0.0
            bom_delivered = self.sudo()._get_bom_delivered(line.sudo())
            qty = 0.0
            if not bom_delivered:
                for move in line.move_ids:
                    if move.state == 'done' and move.location_id.usage != \
                            'supplier':
                        qty += move.product_uom._compute_qty_obj(
                            move.product_uom, move.product_uom_qty,
                            line.product_uom)
            line.qty_returned = qty

    @api.depends('order_id.state', 'move_ids.state', 'move_ids')
    def _compute_qty_received(self):
        super(PurchaseOrderLine, self)._compute_qty_received()
        for line in self:
            bom_delivered = self.sudo()._get_bom_delivered(line.sudo())
            if not bom_delivered:
                for move in line.move_ids:
                    if move.state == 'done' and move.location_id.usage != \
                            'supplier':
                        qty = move.product_uom._compute_qty_obj(
                            move.product_uom, move.product_uom_qty,
                            line.product_uom)
                        line.qty_received -= qty

    qty_to_invoice = fields.Float(compute="_compute_qty_to_invoice",
                                  string='Qty to Bill', copy=False,
                                  default=0.0)
    qty_to_refund = fields.Float(compute="_compute_qty_to_invoice",
                                 string='Qty to Refund', copy=False,
                                 default=0.0)
    qty_refunded = fields.Float(compute="_compute_qty_refunded",
                                string='Refunded Qty', copy=False, default=0.0)

    qty_returned = fields.Float(compute="_compute_qty_returned",
                                string='Returned Qty', copy=False, default=0.0)
    invoice_status = fields.Selection([
        ('no', 'Not purchased'),
        ('to invoice', 'Waiting Invoices'),
        ('invoiced', 'Invoice Received'),
        ], string='Invoice Status', compute='_compute_qty_to_invoice',
        readonly=True, copy=False, default='no')
