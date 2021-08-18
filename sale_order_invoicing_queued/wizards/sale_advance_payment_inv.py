# Copyright 2019-2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, exceptions, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def enqueue_invoices(self):
        queue_obj = self.env["queue.job"]
        order_obj = self.env["sale.order"]
        context = self.env.context
        final = self.advance_payment_method == "all"
        if self.advance_payment_method not in {"delivered", "all"}:
            # Call standard method in these cases
            return self.create_invoices()
        sale_orders = order_obj.browse(context.get("active_ids", []))
        grouped_orders = defaultdict(lambda: order_obj.browse())
        for order in sale_orders:
            # If we have `sale_order_invoicing_grouping_criteria` module
            # installed, we take that grouping criteria
            if hasattr(order, "_get_sale_invoicing_group_key"):
                group_key = order._get_sale_invoicing_group_key()
            else:
                # HACK: This is not exactly doing the same as upstream, as we
                # apply fields over order, not invoice vals, but serves for
                # standard case and most of the transferred fields mapping them.
                # This is done this way for not needing to build 2 times the
                # same vals dictionary.
                field_mapping = {"partner_id": "partner_invoice_id"}
                group_key = tuple(
                    [
                        order[field_mapping.get(grouping_key, grouping_key)]
                        for grouping_key in order._get_invoice_grouping_keys()
                    ]
                )
            if order.invoicing_job_ids.filtered(
                lambda x: x.state in {"pending", "enqueued", "started"}
            ):
                raise exceptions.UserError(
                    _(
                        "There's already an enqueued job for invoicing the sales "
                        "order %s. Please wait until it's finished or remove it "
                        "from the selection."
                    )
                    % (order.name,)
                )
            grouped_orders[group_key] |= order
        for orders in grouped_orders.values():
            new_delay = orders.with_delay().create_invoices_job(final)
            job = queue_obj.search([("uuid", "=", new_delay.uuid)])
            orders.sudo().write({"invoicing_job_ids": [(4, job.id)]})
