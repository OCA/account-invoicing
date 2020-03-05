# Copyright 2019-2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoice_grouping_keys(self):
        """Inject the extra grouping criteria."""
        group_key = super()._get_invoice_grouping_keys()
        criteria = (
            self.partner_id.sale_invoicing_grouping_criteria_id
            or self.company_id.default_sale_invoicing_grouping_criteria_id
        )
        for field in criteria.field_ids:
            group_key.append(field.name)
        return group_key
