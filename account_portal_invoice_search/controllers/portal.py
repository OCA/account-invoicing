# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.http import request, route

from odoo.addons.account.controllers.portal import PortalAccount
from odoo.addons.portal.controllers.portal import pager as portal_pager


class PortalAccount(PortalAccount):
    @route()
    def portal_my_invoices(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        """Inject search term in the context so it can be used in the search method
        in account.move to filter invoices from the portal"""
        if "search" in kw:
            context = dict(request.env.context)
            context.update({"portal_invoice_filter": kw.get("search", "")})
            request.env.context = context
        response = super().portal_my_invoices(
            page=page,
            date_begin=date_begin,
            date_end=date_end,
            sortby=sortby,
            filterby=filterby,
            **kw
        )
        response.qcontext.setdefault("searchbar_inputs", {})
        label_search = _("Search in Invoices & Bills")
        pager = portal_pager(
            url="/my/invoices",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "search": kw.get("search"),
                "search_in": "portal_invoice_filter",
            },
            total=self._items_per_page * response.qcontext["pager"]["page_count"],
            page=page,
            step=self._items_per_page,
        )
        response.qcontext["searchbar_inputs"].update(
            {
                "portal_order_filter": {
                    "input": "portal_invoice_filter",
                    "label": label_search,
                },
            }
        )
        response.qcontext["pager"] = pager
        response.qcontext["search_in"] = "portal_invoice_filter"
        return response
