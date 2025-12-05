# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import OrderedDict

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortalBilling(CustomerPortal):
    def _show_report(self, model, report_type, report_ref, download=False):
        if model._name != "account.billing":
            return super()._show_report(model, report_type, report_ref, download)
        billing_report = request.env.user.company_id.billing_portal_report
        if billing_report:
            external_id = billing_report.get_external_id()
            report_ref = external_id.get(billing_report.id)
        return super()._show_report(model, report_type, report_ref, download)

    def _get_billing_domain(self, bill_type=None):
        domain = [("state", "=", "billed")]
        if bill_type:
            domain.append(("bill_type", "=", bill_type))
        return domain

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        Billing = request.env["account.billing"]
        if "customer_bill_count" in counters:
            values["customer_bill_count"] = (
                Billing.search_count(self._get_billing_domain("out_invoice"))
                if Billing.has_access("read")
                else 0
            )
        if "vendor_bill_count" in counters:
            values["vendor_bill_count"] = (
                Billing.search_count(self._get_billing_domain("in_invoice"))
                if Billing.has_access("read")
                else 0
            )
        return values

    def _get_billing_searchbar_sortings(self):
        return {
            "date": {"label": _("Newest"), "order": "create_date desc, id desc"},
            "billing_date": {"label": _("Billing Date"), "order": "date desc, id desc"},
            "name": {"label": _("Name"), "order": "name asc, id asc"},
        }

    def _render_billing_portal(
        self,
        page,
        sortby,
        filterby,
        searchbar_filters,
        default_filter,
    ):
        values = self._prepare_portal_layout_values()
        Billing = request.env["account.billing"]
        domain = self._get_billing_domain()
        searchbar_sortings = self._get_billing_searchbar_sortings()
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]
        if searchbar_filters:
            if not filterby or filterby not in searchbar_filters:
                filterby = default_filter
            domain += searchbar_filters[filterby]["domain"]
        count = Billing.search_count(domain)
        pager = portal_pager(
            url="/my/billings",
            url_args={"sortby": sortby, "filterby": filterby},
            total=count,
            page=page,
            step=self._items_per_page,
        )
        billings = Billing.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_billing_history"] = billings.ids[:100]
        values.update(
            {
                "billings": billings,
                "page_name": "billing",
                "pager": pager,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
                "filterby": filterby,
                "default_url": "/my/billings",
            }
        )
        return request.render("account_billing_portal.portal_my_billings", values)

    @http.route(
        ["/my/billings", "/my/billings/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_billings(self, page=1, sortby=None, filterby=None, **kw):
        return self._render_billing_portal(
            page,
            sortby,
            filterby,
            {
                "all": {
                    "label": _("All"),
                    "domain": [("state", "=", "billed")],
                },
                "out_invoice": {
                    "label": _("Customer Bills"),
                    "domain": [("bill_type", "=", "out_invoice")],
                },
                "in_invoice": {
                    "label": _("Vendor Bills"),
                    "domain": [("bill_type", "=", "in_invoice")],
                },
            },
            "all",
        )

    def _billing_get_page_view_values(self, billing, access_token, **kwargs):
        values = {
            "billing": billing,
            "page_name": "billing",
            "report_type": "html",
        }
        return self._get_page_view_values(
            billing, access_token, values, "my_billing_history", False, **kwargs
        )

    @http.route(
        ["/my/billings/<int:billing_id>"], type="http", auth="public", website=True
    )
    def portal_my_billing(
        self, billing_id, access_token=None, report_type=None, download=False, **kw
    ):
        try:
            billing_sudo = self._document_check_access(
                "account.billing", billing_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        if report_type in ("html", "pdf", "text"):
            pdf_report_name = "account_billing.report_account_billing"
            return self._show_report(
                model=billing_sudo,
                report_type=report_type,
                report_ref=pdf_report_name,
                download=download,
            )
        values = self._billing_get_page_view_values(billing_sudo, access_token, **kw)
        return request.render("account_billing_portal.portal_my_billing", values)
