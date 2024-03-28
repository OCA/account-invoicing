# Copyright 2004-2010 Tiny SPRL (http://tiny.be).
# Copyright 2010-2011 Elico Corp.
# Copyright 2016 Acsone (https://www.acsone.eu/)
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2019 Okia SPRL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class InvoiceMerge(models.TransientModel):
    _name = "invoice.merge"
    _description = "Merge Partner Invoice"

    keep_references = fields.Boolean(
        "Keep references from original invoices", default=True
    )
    date_invoice = fields.Date("Invoice Date")

    @api.model
    def default_get(self, fields_list):
        self._dirty_check()
        return super().default_get(fields_list)

    @api.model
    def _get_not_mergeable_invoices_message(self, invoices):
        """Overridable function to custom error message"""
        move_type_set = set(invoices.mapped("move_type"))
        if "in_invoice" in move_type_set or "in_refund" in move_type_set:
            key_fields = invoices._get_invoice_key_cols_in()
        else:
            key_fields = invoices._get_invoice_key_cols_out()
        # key_fields = invoices._get_invoice_key_cols_out()
        error_msg = {}
        if len(invoices) != len(invoices._get_draft_invoices()):
            error_msg["state"] = _("Mergeable State (ex : %s)") % (
                invoices and fields.first(invoices).state or _("Draft")
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

    def merge_invoices(self):
        """To merge similar type of account invoices.

        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs
        @param context: A standard dictionary

        @return: account invoice action
        """
        inv_obj = self.env["account.move"]
        aw_obj = self.env["ir.actions.act_window"]
        ids = self.env.context.get("active_ids", [])
        invoices = inv_obj.browse(ids)
        allinvoices = invoices.do_merge(
            keep_references=self.keep_references, date_invoice=self.date_invoice
        )
        xid = {
            "out_invoice": "account.action_move_out_invoice_type",
            "out_refund": "account.action_move_out_refund_type",
            "in_invoice": "account.action_move_in_invoice_type",
            "in_refund": "account.action_move_in_refund_type",
        }[fields.first(invoices).move_type]

        res = aw_obj._for_xml_id(xid)
        res["domain"] = [("id", "in", ids + list(allinvoices.keys()))]
        return res
