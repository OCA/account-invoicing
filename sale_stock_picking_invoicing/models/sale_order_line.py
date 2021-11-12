# Copyright (C) 2013-Today - Akretion (<http://www.akretion.com>).
# @author Renato Lima <renato.lima@akretion.com.br>
# @author Raphael Valyi <raphael.valyi@akretion.com>
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        if self.order_id.company_id.sale_invoicing_policy == "stock_picking":
            values["invoice_state"] = "2binvoiced"

        return values
