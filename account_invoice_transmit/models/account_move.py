# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_invoice_to_transmit = fields.Boolean(compute="_compute_is_invoice_to_transmit")

    @api.depends("state", "move_type", "is_move_sent")
    def _compute_is_invoice_to_transmit(self):
        for rec in self:
            if (
                rec.state == "posted"
                and rec.move_type in ("out_invoice", "out_refund")
                and not rec.is_move_sent
            ):
                rec.is_invoice_to_transmit = True
            else:
                rec.is_invoice_to_transmit = False

    def _get_transmit_invoice_by_email_template(self):
        """Return email template used in mass sending"""
        return self.env.ref("account.email_template_edi_invoice")

    def _transmit_invoice(self, method):
        # we need to apply the filter because the state may have
        # changed since when we delayed the job
        invoices = self.exists().filtered("is_invoice_to_transmit")
        if not invoices:
            return self.browse()
        invoices.write({"is_move_sent": True})
        for invoice in invoices:
            invoice.message_post(body=_("Invoice sent by %s") % method)
        return invoices

    def _transmit_invoice_by_post(self):
        """Mass sending by post"""
        invoices = self._transmit_invoice("post")
        invoice_print = self.env["account.invoice.print"].create(
            {"invoice_ids": [(6, 0, invoices.ids)]}
        )
        invoice_print.generate_report()

    def _transmit_invoice_by_email(self):
        """Mass sending by email"""
        invoices = self._transmit_invoice("email")
        for invoice in invoices:
            email_template = self._get_transmit_invoice_by_email_template()
            email_template.send_mail(invoice.id)

    def action_send_and_print(self):
        # Replace standard method by new wizard
        view = self.env.ref("account_invoice_transmit.account_invoice_transmit_view")
        report_action = {
            "name": _("Mass Sending"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.invoice.transmit",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "context": dict(active_model=self._name, active_ids=self.ids),
        }
        return report_action
