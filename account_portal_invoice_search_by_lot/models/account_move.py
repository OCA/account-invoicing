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
            return
        lot_ids = (
            self.env["stock.production.lot"].sudo()._search([("name", "=ilike", value)])
        )
        sml_ids = (
            self.env["stock.move.line"]
            .sudo()
            ._search([("lot_id", "in", lot_ids), ("state", "=", "done")])
        )
        sm = (
            self.env["stock.move"]
            .sudo()
            .search_read([("move_line_ids", "in", sml_ids)], ["sale_line_id"])
        )
        return [
            (
                "line_ids.sale_line_ids",
                "in",
                list({x["sale_line_id"][:1] for x in sm if x["sale_line_id"]}),
            )
        ]

    @api.model
    def _get_portal_search_domain(self, portal_invoice_filter):
        domain = super()._get_portal_search_domain(portal_invoice_filter)
        domain = expression.OR(
            [domain, [("lot_name_search", "=", portal_invoice_filter)]]
        )
        return domain
