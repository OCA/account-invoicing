# Copyright 2019-2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_sale_invoicing_group_key(self):
        """Prepare extended grouping criteria for sales orders."""
        self.ensure_one()
        group_key = [
            self.company_id.id,
            self.partner_invoice_id.id,
            self.currency_id.id,
        ]
        criteria = (
            self.partner_id.sale_invoicing_grouping_criteria_id
            or self.company_id.default_sale_invoicing_grouping_criteria_id
        )
        for field in criteria.field_ids:
            group_key.append(self[field.name])
        return tuple(group_key)

    def _create_invoices(self, grouped=False, final=False):
        """Slice the batch according grouping criteria."""
        order_groups = {}
        for order in self:
            group_key = order._get_sale_invoicing_group_key()
            if group_key not in order_groups:
                order_groups[group_key] = order
            else:
                order_groups[group_key] += order
        moves = self.env["account.move"]
        for group in order_groups.values():
            moves += super(SaleOrder, group)._create_invoices(
                grouped=grouped, final=final
            )
        return moves
