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
        res = self.env["res.partner"]
        for sale in self:
            res += sale.partner_invoice_id or sale.partner_id
        return res

    def _get_invoice_grouping_keys(self):
        res = super()._get_invoice_grouping_keys()
        partners = self._get_grouping_partner()
        criteria = (
            partners.mapped("sale_invoicing_grouping_criteria_id")
            or self.company_id.default_sale_invoicing_grouping_criteria_id
        )
        return res + criteria.sudo().field_ids.mapped("name")
