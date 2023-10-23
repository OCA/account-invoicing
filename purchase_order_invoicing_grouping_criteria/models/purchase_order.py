# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _get_purchase_invoicing_group_key(self):
        """Prepare extended grouping criteria for purchase orders."""
        self.ensure_one()
        group_key = [
            self.company_id.id,
            self.partner_id.id,
            self.currency_id.id,
        ]
        criteria = (
            self.partner_id.purchase_invoicing_grouping_criteria_id
            or self.company_id.default_purchase_invoicing_grouping_criteria_id
        )
        for field in criteria.field_ids.sudo():
            group_key.append(self[field.name])
        return tuple(group_key)

    def action_create_invoice(self):
        """Slice the batch according grouping criteria."""
        order_groups = {}
        for order in self:
            group_key = order._get_purchase_invoicing_group_key()
            if group_key not in order_groups:
                order_groups[group_key] = order
            else:
                order_groups[group_key] += order
        moves = self.env["account.move"]
        for group in order_groups.values():
            action = super(PurchaseOrder, group).action_create_invoice()
            if action.get("res_id", False):
                moves += moves.browse(action["res_id"])
        return self.action_view_invoice(moves)
