# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
        compute="_compute_warehouse_id",
        store=True,
    )

    @api.depends(
        "sale_line_ids",
        "sale_line_ids.order_id.warehouse_id",
        "purchase_line_id",
        "purchase_line_id.order_id.picking_type_id.warehouse_id",
    )
    def _compute_warehouse_id(self):
        for line in self:
            line.warehouse_id = line._get_warehouse()

    def _get_warehouse(self):
        """Compute the warehouse for this invoice line.

        Returns the warehouse if all linked sale or purchase order lines
        share the same warehouse, False otherwise.
        Can be overridden to add custom logic.
        """
        self.ensure_one()
        if self.sale_line_ids:
            warehouses = self.sale_line_ids._get_warehouse()
            if len(warehouses) == 1:
                return warehouses
        elif self.purchase_line_id:
            return self.purchase_line_id._get_warehouse()
        return False
