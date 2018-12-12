# Copyright 2017 Eficent Business and IT Consulting Services
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import collections
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    invoice_refund_count = fields.Integer(
        compute="_compute_invoice_refund_count",
        string='# of Invoice Refunds',
    )

    @api.depends('order_line.qty_returned', 'order_line.qty_refunded')
    def _get_invoiced(self):
        """Modify invoice_status for taking into account returned/refunded
        qty. It's only needed to modify the method for resetting state to
        "to invoice", as the rest of the states are already handled by super.
        """
        super(PurchaseOrder, self)._get_invoiced()
        for order in self.filtered(lambda x: x.state in ('purchase', 'done')):
            if any(x.qty_received - x.qty_invoiced for x in order.order_line):
                order.invoice_status = 'to invoice'

    @api.depends('order_line.invoice_lines.invoice_id.state')
    def _compute_invoice_refund_count(self):
        for order in self:
            invoices = order.mapped(
                'order_line.invoice_lines.invoice_id'
            ).filtered(lambda x: x.type == 'in_refund')
            order.invoice_refund_count = len(invoices)

    @api.depends('invoice_refund_count')
    def _compute_invoice(self):
        """Change computation for excluding refund invoices.

        Make this compatible with other extensions, only subtracting refunds
        from the number obtained in super.
        """
        super()._compute_invoice()
        for order in self:
            order.invoice_count -= order.invoice_refund_count

    @api.multi
    def action_view_invoice_refund(self):
        """This function returns an action that display existing vendor refund
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
        if len(refunds) > 1:
            result['domain'] = [('id', 'in', refunds.ids)]
        elif len(refunds) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = refunds.id
        return result

    @api.multi
    def action_view_invoice(self):
        """Change super action for displaying only normal invoices."""
        result = super(PurchaseOrder, self).action_view_invoice()
        invoices = self.invoice_ids.filtered(
            lambda x: x.type == 'in_invoice'
        )
        # choose the view_mode accordingly
        if len(invoices) != 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = invoices.id
        return result


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_refunded = fields.Float(
        compute="_compute_qty_refunded",
        string='Refunded Qty',
    )
    qty_returned = fields.Float(
        compute="_compute_qty_returned",
        string='Returned* Qty',
        help="This is ONLY the returned quantity that is refundable.",
        store=True,
    )

    @api.depends('invoice_lines.invoice_id.state',
                 'invoice_lines.quantity')
    def _compute_qty_refunded(self):
        for line in self:
            inv_lines = line.invoice_lines.filtered(lambda x: (
                (x.invoice_id.type == 'in_invoice' and x.quantity < 0.0) or
                (x.invoice_id.type == 'in_refund' and x.quantity > 0.0)
            ))
            line.qty_refunded = sum(inv_lines.mapped(lambda x: (
                x.uom_id._compute_quantity(x.quantity, line.product_uom)
            )))

    @api.depends(
        'move_ids.state',
        'move_ids.returned_move_ids.state',
    )
    def _compute_qty_returned(self):
        """Made through read_group for not impacting in performance."""
        ProductUom = self.env['uom.uom']
        groups = self.env['stock.move'].read_group(
            [('purchase_line_id', 'in', self.ids),
             ('state', '=', 'done'),
             ('to_refund', '=', True),
             ('location_id.usage', '!=', 'supplier')],
            ['purchase_line_id', 'product_uom_qty', 'product_uom'],
            ['purchase_line_id', 'product_uom'], lazy=False,
        )
        p = self._prefetch
        # load all UoM records at once on first access
        uom_ids = set(g['product_uom'][0] for g in groups)
        ProductUom.browse(list(uom_ids), prefetch=p)
        line_qtys = collections.defaultdict(lambda: 0)
        for g in groups:
            uom = ProductUom.browse(g["product_uom"][0], prefetch=p)
            line = self.browse(g['purchase_line_id'][0], prefetch=p)
            if uom == line.product_uom:
                qty = g["product_uom_qty"]
            else:
                qty = uom._compute_quantity(
                    g["product_uom_qty"], line.product_uom,
                )
            line_qtys[line.id] += qty
        for line in self:
            line.qty_returned = line_qtys.get(line.id, 0)
