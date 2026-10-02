# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class AccountMove(models.Model):
    _inherit = "account.move"

    lot_name_search = fields.Char(
        compute="_compute_lot_name_search", search="_search_lot_name_search"
    )

    def _compute_lot_name_search(self):
        """We just need the field to use the search"""

    def _search_lot_name_search(self, operator, value):
        """Used for portal search. We force equality as we handle millions of records.
        A fuzzy search could lead to a huge performance drop. So we force a exact match.
        """
        if operator != "=":
            return [("id", "=", False)]

        lots = self.env["stock.lot"].sudo().search([("name", "ilike", value)])
        if not lots:
            return [("id", "=", False)]

        move_lines = (
            self.env["stock.move.line"]
            .sudo()
            .search([("lot_id", "in", lots.ids), ("state", "=", "done")])
        )
        if not move_lines:
            return [("id", "=", False)]

        sale_line_ids = move_lines.mapped("move_id.sale_line_id").ids
        if not sale_line_ids:
            return [("id", "=", False)]

        return [("line_ids.sale_line_ids", "in", sale_line_ids)]

    @api.model
    def _get_portal_search_domain(self, portal_invoice_filter):
        domain = super()._get_portal_search_domain(portal_invoice_filter)
        domain = expression.OR(
            [domain, [("lot_name_search", "=", portal_invoice_filter)]]
        )
        return domain
