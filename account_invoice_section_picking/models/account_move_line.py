# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def _get_section_group(self):
        group = super()._get_section_group()
        # If product is invoiced by delivered quantities:
        #  - filter on done pickings to avoid displaying backorders
        #  - Remove pickings linked with same sale order lines if an invoice
        #    was created after its date_done
        invoice_section_grouping = self.env.company.invoice_section_grouping
        if (
            invoice_section_grouping == "delivery_picking"
            and self.product_id.invoice_policy == "delivery"
        ):
            last_invoice_line = self.search(
                [
                    ("sale_line_ids", "in", self.sale_line_ids.ids),
                    ("id", "not in", self.ids),
                ],
                order="create_date",
                limit=1,
            )
            pickings_already_invoiced = self.env["stock.picking"].search(
                [
                    ("date_done", "<=", last_invoice_line.create_date),
                    ("id", "in", self.sale_line_ids.mapped("order_id.picking_ids").ids),
                ]
            )
            group = group.filtered(
                lambda p: p.state == "done"
                and p.id not in pickings_already_invoiced.ids
            )
        return group

    @api.model
    def _get_section_grouping(self):
        invoice_section_grouping = self.env.company.invoice_section_grouping
        if invoice_section_grouping == "delivery_picking":
            return "sale_line_ids.move_ids.picking_id"
        return super()._get_section_grouping()
