# Copyright 2020 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from collections import OrderedDict

from odoo import _, http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import content_disposition, request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class PortalAccount(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "invoice_count" in counters:
            invoice_count = (
                request.env["account.move"].search_count(
                    [
                        (
                            "move_type",
                            "in",
                            ("out_invoice", "in_invoice", "out_refund", "in_refund"),
                        ),
                    ]
                )
                if request.env["account.move"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
            values["invoice_count"] = invoice_count
        if "receipt_count" in counters:
            receipt_count = (
                request.env["account.move"].search_count(
                    [
                        ("move_type", "in", ("out_receipt", "in_receipt")),
                    ]
                )
                if request.env["account.move"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
            values["receipt_count"] = receipt_count

        return values

    def _receipt_get_page_view_values(self, receipt, access_token, **kwargs):
        values = {
            "page_name": "receipt",
            "receipt": receipt,
        }
        return self._get_page_view_values(
            receipt, access_token, values, "my_receipts_history", False, **kwargs
        )

    @http.route(
        ["/my/receipts", "/my/receipts/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_receipts(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        AccountReceipt = request.env["account.move"]

        domain = [("move_type", "in", ("out_receipt", "in_receipt"))]

        searchbar_sortings = {
            "date": {"label": _("Date"), "order": "invoice_date desc"},
            "name": {"label": _("Reference"), "order": "name desc"},
            "state": {"label": _("Status"), "order": "state"},
        }
        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        searchbar_filters = {
            "all": {
                "label": _("All"),
                "domain": [("move_type", "in", ["in_receipt", "out_receipt"])],
            },
            "sale_receipts": {
                "label": _("Sale Receipts"),
                "domain": [("move_type", "=", "out_receipt")],
            },
            "purchase_receipts": {
                "label": _("Purchase Receipts"),
                "domain": [("move_type", "=", "in_receipt")],
            },
        }
        # default filter by value
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        # count for pager
        receipt_count = AccountReceipt.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/receipts",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=receipt_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        receipts = AccountReceipt.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_receipts_history"] = receipts.ids[:100]

        values.update(
            {
                "date": date_begin,
                "receipts": receipts,
                "page_name": "receipt",
                "pager": pager,
                "default_url": "/my/receipts",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
                "filterby": filterby,
            }
        )
        return request.render("account_portal_receipt.portal_my_receipts", values)

    @http.route(
        ["/my/receipts/<int:receipt_id>"], type="http", auth="public", website=True
    )
    def portal_receipt_detail(
        self, receipt_id, access_token=None, report_type=None, download=False, **kw
    ):
        try:
            receipt_sudo = self._document_check_access(
                "account.move", receipt_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=receipt_sudo,
                report_type=report_type,
                report_ref="account_receipt_print.account_receipts",
                download=download,
            )

        values = self._receipt_get_page_view_values(receipt_sudo, access_token, **kw)
        acquirers = values.get("acquirers")
        if acquirers:
            country_id = (
                values.get("partner_id") and values.get("partner_id")[0].country_id.id
            )
            values["acq_extra_fees"] = acquirers.get_acquirer_extra_fees(
                receipt_sudo.amount_residual, receipt_sudo.currency_id, country_id
            )

        return request.render("account_portal_receipt.portal_receipt_page", values)

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_ref == "account_receipt_print.account_receipts" and download:
            if report_type not in ("html", "pdf", "text"):
                raise UserError(_("Invalid report type: %s", report_type))

            report_sudo = request.env.ref(report_ref).sudo()

            if not isinstance(report_sudo, type(request.env["ir.actions.report"])):
                raise UserError(_("%s is not the reference of a report", report_ref))

            method_name = "_render_qweb_%s" % (report_type)
            report = getattr(report_sudo, method_name)(
                [model.id], data={"report_type": report_type}
            )[0]
            reporthttpheaders = [
                (
                    "Content-Type",
                    "application/pdf" if report_type == "pdf" else "text/html",
                ),
                ("Content-Length", len(report)),
            ]
            if report_type == "pdf" and download:
                filename = "%s.pdf" % (
                    re.sub(r"\W+", "-", model._get_move_display_name())
                )
                reporthttpheaders.append(
                    ("Content-Disposition", content_disposition(filename))
                )
            return request.make_response(report, headers=reporthttpheaders)
        return super(PortalAccount, self)._show_report(
            model, report_type, report_ref, download
        )
