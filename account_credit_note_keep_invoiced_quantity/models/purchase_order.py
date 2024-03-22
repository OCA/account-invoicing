# Copyright 2023 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _compute_invoice(self):
        """Include all reversals that may not be linked on the line level."""
        if not self.ids:
            return
        self.env.cr.execute(
            """
            with recursive invoices (purchase_id, move_id) AS (
                select distinct on (pol.order_id, aml.move_id)
                    pol.order_id, aml.move_id
                from purchase_order_line pol
                join account_move_line aml
                    on aml.purchase_line_id = pol.id
                where pol.order_id in %s
                union all
                select invoices.purchase_id, am2.id
                from account_move am2
                join invoices on invoices.move_id = am2.reversed_entry_id
            )
            select distinct on (purchase_id, move_id) * from invoices;
            """,
            (tuple(self.ids),),
        )
        purchase2move = {}
        for purchase_id, move_id in self.env.cr.fetchall():
            purchase2move.setdefault(purchase_id, []).append(move_id)
        for purchase in self:
            purchase.invoice_ids = self.env["account.move"].browse(
                purchase2move.get(purchase.id, [])
            )
            purchase.invoice_count = len(purchase.invoice_ids)
