# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.http import route

from odoo.addons.account.controllers.portal import PortalAccount
from odoo.addons.portal.controllers.portal import pager as portal_pager


class PortalAccount(PortalAccount):
    def get_account_invoice_domain(self, response, kw, name):
        return [
            ('id', 'in', response.qcontext[name].ids),
            '|',
            ('number', 'ilike', kw['search']),
            ('state', 'ilike', kw['search'])
        ]

    @route()
    def portal_my_invoices(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        """Inject search term in the context so it can be used in the search
        method in account.move to filter invoices from the portal"""
        response = super().portal_my_invoices(
            page=page,
            date_begin=date_begin,
            date_end=date_end,
            sortby=sortby,
            **kw,
        )
        name = 'invoices'
        if "search" in kw:
            domain = self.get_account_invoice_domain(response, kw, name)
            invoices = response.qcontext[name].search(domain)
            response.qcontext[name] = invoices
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
            total=len(response.qcontext.get('invoices', 0)),
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
