# Copyright (C) 2020 - TODAY, Elego Software Solutions GmbH, Berlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import fields, models, exceptions, _

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    approval_requested = fields.Boolean(
        string="Approval requested",
        copy=False,
    )

    approval_authorized = fields.Boolean(
        compute="_compute_approval_process",
    )

    approval_needed = fields.Boolean(
        compute="_compute_approval_process",
    )

    approval_process_ids = fields.One2many(
        "account.approval.process",
        string="Approval processes",
        compute="_compute_approval_process_ids",
    )

    current_approval_process_id = fields.Many2one(
        comodel_name="account.approval.process",
        string="Actual approval process",
        compute="_compute_current_approval_process_id",
        readonly=True,
    )

    completed_approval_process_id = fields.Many2one(
        comodel_name="account.approval.process",
        string="Completed approval process",
        readonly=True,
        copy=False,
    )

    approval_process_progress_current_step = fields.Integer(
        string="Approval process progress (current step)",
        compute="_compute_approval_process_progress",
        readonly=True,
    )

    approval_process_progress_last_step = fields.Integer(
        string="Approval process progress (last step)",
        compute="_compute_approval_process_progress",
        readonly=True,
    )

    approval_process_progress_percent = fields.Float(
        string="Approval process progress (percent)",
        compute="_compute_approval_process_progress",
        readonly=True,
    )

    def _compute_approval_process_progress(self):
        for invoice in self.filtered(lambda inv: inv.state == "draft"):
            p_step = current_step = last_step = len(invoice.approval_process_ids)
            if invoice.current_approval_process_id:
                p_step = current_step = invoice.approval_process_ids.ids.index(
                    invoice.current_approval_process_id.id
                )
                if invoice.approval_requested:
                    p_step += 0.5

            percent = p_step * 100 / last_step if last_step else 0
            invoice.approval_process_progress_current_step = current_step
            invoice.approval_process_progress_last_step = last_step
            invoice.approval_process_progress_percent = percent

    def _compute_approval_process_ids(self):
        obj_ap = self.env["account.approval.process"]
        for invoice in self:
            field_name = "company_id"
            field_val = invoice.company_id
            if invoice.journal_id.overwrite_company_settings:
                field_name = "journal_id"
                field_val = invoice.journal_id

            domain = [
                ("invoice_type", "=", invoice.type),
                (field_name, "=", field_val.id),
                ("validation_amount_from", "<=", invoice.amount_untaxed),
                "|",
                ("validation_amount_to", "=", -1.0),
                ("validation_amount_to", ">=", invoice.amount_untaxed),
            ]
            _logger.debug(
                "_compute_approval_process_ids: invoice=%s, domain=%s", invoice, domain
            )
            ids = obj_ap.search(domain).ids
            invoice.approval_process_ids = ids if ids else False

    def _compute_current_approval_process_id(self):
        for invoice in self:
            current_ap_id = last_id = self.env["account.approval.process"]
            aps = invoice.approval_process_ids
            if invoice.state == "draft" and aps:
                if invoice.completed_approval_process_id is not False:
                    for ap in aps:
                        if last_id == invoice.completed_approval_process_id:
                            current_ap_id = ap
                            break
                        last_id = ap
            invoice.current_approval_process_id = current_ap_id.id

    def _compute_approval_process(self):
        for invoice in self:
            approval_needed = False
            approval_authorized = False
            aps = invoice.approval_process_ids
            if invoice.state == "draft" and aps:
                approval_needed = aps[-1] != invoice.completed_approval_process_id
                current_id = invoice.current_approval_process_id
                approval_authorized = current_id.has_current_user_access_rights()

            invoice.approval_needed = approval_needed
            invoice.approval_authorized = approval_needed & approval_authorized

    def action_invoice_request_approval(self):
        found_invoices = self.filtered(
            lambda inv: inv.state != "draft" or not inv.approval_needed
        )
        if found_invoices:
            msg = _(
                "One or more invoice do not require approval.\nInvoices (ids):\n{ids}"
            )
            invoice_ids = ",\n".join([str(i.id) for i in found_invoices])
            raise exceptions.UserError(msg.format(ids=invoice_ids))

        for inv in self:
            current_ap = inv.current_approval_process_id
            if current_ap.email_template_id:
                current_ap.email_template_id.send_mail(inv.id, force_send=True)
            else:
                msg = _("Approval '{name}' requested.")
                inv.message_post(body=msg.format(name=current_ap.name))
            inv.approval_requested = True

    def action_invoice_approve(self):
        found_invoices = self.filtered(lambda inv: inv.state != "draft")
        if found_invoices:
            msg = _(
                "Invoices must be in draft state in order to approve it.\nInvoices:"
                "\n{ids}"
            )
            invoice_names = ",\n".join([i.number for i in found_invoices if i])
            raise exceptions.UserError(msg.format(ids=invoice_names))

        to_open_invoices = self.filtered(lambda inv: inv.state == "draft")
        found_invoices = to_open_invoices.filtered(
            lambda inv: inv.approval_needed is False
        )
        if found_invoices:
            msg = _(
                "One or more invoice do not require approval.\nInvoices (ids):\n{ids}"
            )
            invoice_ids = ",\n".join([str(i.id) for i in found_invoices])
            raise exceptions.UserError(msg.format(ids=invoice_ids))

        found_invoices = to_open_invoices.filtered(
            lambda inv: inv.approval_authorized is False
        )
        if found_invoices:
            msg = _(
                "You have no rights to approval one or more invoices.\nInvoices (ids):"
                "\n{ids}"
            )
            invoice_ids = ",\n".join([str(i.id) for i in found_invoices])
            raise exceptions.UserError(msg.format(ids=invoice_ids))

        for inv in to_open_invoices:
            msg = _("'{test}' approved.")
            values = {
                "approval_requested": False,
                "completed_approval_process_id": inv.current_approval_process_id.id,
            }
            inv.write(values)
            inv.message_post(body=msg.format(test=inv.current_approval_process_id.name))

    def action_invoice_open(self):
        to_open_invoices = self.filtered(lambda inv: inv.approval_needed is True)
        if to_open_invoices:
            msg = _("One or more invoice do require approval.\nInvoices (ids):\n{ids}")
            invoice_ids = ",\n".join([str(i.id) for i in to_open_invoices])
            raise exceptions.UserError(msg.format(ids=invoice_ids))
        return super(AccountInvoice, self).action_invoice_open()
