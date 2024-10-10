# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2018 Camptocamp SA
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo import _, fields, models


class AccountInvoicePrint(models.Model):
    _name = "account.invoice.print"
    _rec_name = "create_date"
    _description = "Invoices sending report"

    invoice_ids = fields.Many2many("account.move", readonly=True)
    document = fields.Binary(
        comodel_name="ir.attachment", attachment=True, readonly=True
    )
    fname = fields.Char(compute="_compute_file_name")
    state = fields.Selection(
        selection=[("progress", "In Progress"), ("done", "Done")],
        required=True,
        readonly=True,
        default="progress",
    )

    def _compute_file_name(self):
        for record in self:
            record.fname = f"invoice_print_{record.id}.pdf"

    def _notify_report_generated(self):
        self.ensure_one()
        action_xmlid = "account_invoice_transmit.action_account_invoice_print_form"
        action = self.env["ir.actions.act_window"]._for_xml_id(action_xmlid)
        action.update({"res_id": self.id, "views": [(False, "form")]})
        self.env.user.notify_info(
            _("A report for printing the invoices is available."),
            sticky=True,
            action=action,
        )

    def generate_report(self):
        """Generate a pdf report for all invoices."""
        self.ensure_one()
        content, _content_type = self.env["ir.actions.report"]._render_qweb_pdf(
            "account.report_invoice", self.invoice_ids.ids, False
        )
        self.document = base64.b64encode(content)
        self._notify_report_generated()
        self.state = "done"
        return _("Invoice generation has succeeded")

    def action_view_invoice(self):
        invoices = self.mapped("invoice_ids")
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        if len(invoices) > 1:
            action["domain"] = [("id", "in", invoices.ids)]
        elif len(invoices) == 1:
            action["views"] = [(self.env.ref("account.invoice_form").id, "form")]
            action["res_id"] = invoices.ids[0]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action
