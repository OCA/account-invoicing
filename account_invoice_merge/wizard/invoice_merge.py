# Copyright 2004-2010 Tiny SPRL (http://tiny.be).
# Copyright 2010-2011 Elico Corp.
# Copyright 2016 Acsone (https://www.acsone.eu/)
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2019 Okia SPRL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class InvoiceMerge(models.TransientModel):
    _name = "invoice.merge"
    _description = "Merge Partner Invoice"

    keep_references = fields.Boolean(
        "Keep references from original invoices", default=True
    )
    date_invoice = fields.Date("Invoice Date")

    @api.model
    def _get_not_mergeable_invoices_message(self, invoices):
        """Overridable function to custom error message"""
        key_fields = invoices._get_invoice_key_cols()
        error_msg = {}
        if len(invoices) != len(invoices._get_draft_invoices()):
            error_msg["state"] = _("Merge-able State (ex : %s)") % (
                invoices and invoices[0].state or _("Draft")
            )
        for field in key_fields:
            if len(set(invoices.mapped(field))) > 1:
                error_msg[field] = invoices._fields[field].string
        return error_msg

    @api.model
    def _dirty_check(self):
        if self.env.context.get("active_model", "") == "account.move":
            ids = self.env.context["active_ids"]
            if len(ids) < 2:
                raise UserError(
                    _("Please select multiple invoices to merge in the list " "view.")
                )

            invs = self.env["account.move"].browse(ids)
            error_msg = self._get_not_mergeable_invoices_message(invs)
            if error_msg:
                all_msg = _("All invoices must have the same: \n")
                all_msg += "\n".join([value for value in error_msg.values()])
                raise UserError(all_msg)
        return {}

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """Changes the view dynamically
        @param self: The object pointer.
        @return: New arch of view.
        """
        res = super(InvoiceMerge, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False
        )
        self._dirty_check()
        return res

    def merge_invoices(self):
        """To merge similar type of account invoices.
        @param self: The object pointer.
        @return: account invoice action
        """
        ids = self.env.context.get("active_ids", [])
        invoices = self.env["account.move"].browse(
            self.env.context.get("active_ids", [])
        )
        allinvoices = invoices.do_merge(
            keep_references=self.keep_references, date_invoice=self.date_invoice
        )
        xid = {
            "out_invoice": "action_move_out_invoice_type",
            "out_refund": "action_move_out_refund_type",
            "in_invoice": "action_move_in_invoice_type",
            "in_refund": "action_move_in_refund_type",
        }[invoices[0].move_type]
        action = self.env["ir.actions.act_window"]._for_xml_id("account.{}".format(xid))
        action.update(
            {
                "domain": [("id", "in", ids + list(allinvoices.keys()))],
            }
        )
        return action
