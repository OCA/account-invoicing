# Copyright 2023 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiced(self):
        """Include all reversals that may not be linked on the line level."""
        if not self.ids:
            return
        self.env.cr.execute(
            """
            with recursive invoices (sale_id, move_id) AS (
                select distinct on (sol.order_id, am.id) sol.order_id, am.id
                from sale_order_line sol
                join sale_order_line_invoice_rel rel
                    on rel.order_line_id = sol.id
                join account_move_line aml
                    on aml.id = rel.invoice_line_id
                join account_move am on am.id = aml.move_id
                where order_id in %s
                   and am.move_type in ('out_invoice', 'out_refund')
                union all
                select invoices.sale_id, am2.id
                from account_move am2
                join invoices on invoices.move_id = am2.reversed_entry_id
            )
            select distinct on (sale_id, move_id) * from invoices;
            """,
            (tuple(self.ids),),
        )
        sale2move = {}
        for sale_id, move_id in self.env.cr.fetchall():
            sale2move.setdefault(sale_id, []).append(move_id)
        for order in self:
            order.invoice_ids = self.env["account.move"].browse(
                sale2move.get(order.id, [])
            )
            order.invoice_count = len(order.invoice_ids)

    def _search_invoice_ids(self, operator, value):
        """
        Include results based on reversals that may not be linked on the line level.
        """
        if operator == "=" and value and isinstance(value, int):
            operator = "in"
            value = [value]
        if operator == "in" and value and isinstance(value, (list, tuple)):
            self.env.cr.execute(
                """
                with recursive invoices (move_id, reversed_entry_id) as (
                    select am.id, am.reversed_entry_id
                    from account_move am
                    where am.id in %s
                    union all
                    select am.id, am.reversed_entry_id
                    from account_move am
                    join invoices on invoices.reversed_entry_id = am.id
                )
                select sol.order_id
                from sale_order_line sol
                join sale_order_line_invoice_rel rel
                    on rel.order_line_id = sol.id
                join account_move_line aml
                    on aml.id = rel.invoice_line_id
                join account_move am
                    on am.id = aml.move_id
                join invoices on invoices.move_id = am.id
                where am.move_type in ('out_invoice', 'out_refund')
                """,
                (tuple(value),),
            )
            order_ids = [row[0] for row in self.env.cr.fetchall()]
            return [("id", "in", order_ids)]
        return super()._search_invoice_ids(operator, value)
