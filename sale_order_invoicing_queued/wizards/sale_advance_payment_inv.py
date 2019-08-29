# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, models
from collections import defaultdict


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def enqueue_invoices(self):
        queue_obj = self.env['queue.job']
        order_obj = self.env['sale.order']
        context = self.env.context
        final = (self.advance_payment_method == 'all')
        if (self.advance_payment_method not in {'delivered', 'all'}):
            # Call standard method in these cases
            return self.create_invoices()
        sale_orders = order_obj.browse(context.get('active_ids', []))
        grouped_orders = defaultdict(lambda: order_obj.browse())
        for order in sale_orders:
            group_key = (order.partner_invoice_id.id, order.currency_id.id)
            if order.invoicing_job_ids.filtered(
                lambda x: x.state in {'pending', 'enqueued', 'started'}
            ):
                raise exceptions.UserError(_(
                    "There's already an enqueued job for invoicing the sales "
                    "order %s. Please wait until it's finished or remove it "
                    "from the selection."
                ) % (order.name, ))
            grouped_orders[group_key] |= order
        for orders in grouped_orders.values():
            new_delay = orders.sudo().with_delay().create_invoices_job(final)
            job = queue_obj.search([('uuid', '=', new_delay.uuid)])
            orders.sudo().write({'invoicing_job_ids': [(4, job.id)]})
