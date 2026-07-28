# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        new_moves = super()._create_invoices(grouped=grouped, final=final, date=date)
        self._try_link_refund_with_invoice(new_moves)
        return new_moves

    def _try_link_refund_with_invoice(self, new_moves):
        """Try to link the refund to the original invoice
        if there is exactly one candidate."""
        for refund in new_moves.filtered(lambda move: move.move_type == "out_refund"):
            candidate_invoices = (
                refund.invoice_line_ids.sale_line_ids.invoice_lines.move_id.filtered(
                    lambda move: move.state != "cancel"
                    and move.move_type == "out_invoice"
                )
            )
            if len(candidate_invoices) == 1:
                refund.reversed_entry_id = candidate_invoices
                candidate_invoices.message_post(
                    body=self.env._(
                        "This entry has been %s",
                        refund._get_html_link(title=self.env._("reversed")),
                    ),
                )
                refund.message_post(
                    body=candidate_invoices._get_copy_message_content(
                        default={"reversed_entry_id": candidate_invoices}
                    )
                )
