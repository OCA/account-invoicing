# Copyright 2024 Sergio Zanchetta - PNLUG APS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import OrderedDict

from odoo import _, http
from odoo.http import request

from odoo.addons.account.controllers.portal import PortalAccount


class PortalAccount(PortalAccount):
    @http.route()
    def portal_my_invoices(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        res = super(PortalAccount, self).portal_my_invoices(filterby=None)
        values = res.qcontext

        AccountInvoice = request.env["account.move"]

        domain = self._get_invoices_domain()

        searchbar_sortings = values.get("searchbar_sortings", {})

        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        searchbar_filters = values.get("searchbar_filters", {})
        searchbar_filters.update(
            {
                "sale_receipts": {
                    "label": _("Sale Receipts"),
                    "domain": [("move_type", "=", "out_receipt")],
                },
                "purchase_receipts": {
                    "label": _("Purchase Receipts"),
                    "domain": [("move_type", "=", "in_receipt")],
                },
            }
        )

        # default filter by value
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]

        pager = values.get("pager")

        # content according to pager and archive selected
        invoices = AccountInvoice.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_invoices_history"] = invoices.ids[:100]

        values.update(
            {
                "invoices": invoices,
                "sortby": sortby,
                "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
                "filterby": filterby,
            }
        )
        return request.render("account.portal_my_invoices", values)
