# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_portal_search_domain(self, portal_invoice_filter):
        return (
            "|",
            ("name", "ilike", portal_invoice_filter),
            ("payment_reference", "ilike", portal_invoice_filter),
        )

    def _search(self, domain, offset=0, limit=None, order=None):
        """Override to add portal invoice filter to search domain."""
        portal_invoice_filter = self.env.context.get("portal_invoice_filter")
        if portal_invoice_filter:
            portal_search_domain = self._get_portal_search_domain(portal_invoice_filter)
            domain = expression.AND([domain, portal_search_domain])
        return super()._search(domain, offset=offset, limit=limit, order=order)
