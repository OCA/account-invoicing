# Copyright 2019-2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_grouping_partner(self):
        """
        Get the partner who contains the grouping criteria.
        On sale.order, the default should be the invoice address.
        If not set, use the partner_id.
        :return: res.partner recordset
        """
        self.ensure_one()
        return self.partner_invoice_id or self.partner_id

    def _get_sale_invoicing_group_key(self):
        """Prepare extended grouping criteria for sales orders."""
        self.ensure_one()
        group_key = [
            self.company_id.id,
            self.partner_invoice_id.id,
            self.currency_id.id,
        ]
        partner = self._get_grouping_partner()
        criteria = (
            partner.sale_invoicing_grouping_criteria_id
            or self.company_id.default_sale_invoicing_grouping_criteria_id
        )
        for field in criteria.field_ids:
            group_key.append(self[field.name])
        return tuple(group_key)

    def _create_invoices(self, grouped=False, final=False, date=None):
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
                grouped=grouped, final=final, date=date
            )
        return moves
