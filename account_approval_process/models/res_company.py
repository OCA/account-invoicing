# Copyright (C) 2020 - TODAY, Elego Software Solutions GmbH, Berlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, fields, models, _


class Company(models.Model):
    _inherit = "res.company"

    account_approval_process_ids = fields.One2many(
        comodel_name="account.approval.process",
        inverse_name="company_id",
        string="Approval processes",
        context={
            "active_test": False,
        },
    )

    has_invoices_for_reset = fields.Boolean(
        compute="_compute_has_invoices_for_reset",
    )

    @api.constrains("account_approval_process_ids")
    def _check_validation_amount(self):
        processes = self.account_approval_process_ids
        for invoice_type in processes.mapped("invoice_type"):
            if processes and not processes.filtered(
                lambda rc: rc.invoice_type == invoice_type
                and rc.validation_amount_to == -1.0
            ):
                type_str = dict(
                    processes.fields_get()["invoice_type"]["selection"]
                ).get(invoice_type)
                msg = _(
                    "At least one step of the type '{type}' must have the value -1 for "
                    "unlimited at the field 'Amount (to)'."
                ).format(type=type_str)
                raise exceptions.ValidationError(msg)

    def _get_domain_invoices_for_reset(self, ids):
        return [
            "&",
            ("state", "=", "draft"),
            "&",
            ("journal_id.company_id", "=" if isinstance(ids, int) else "in", ids),
            "&",
            ("journal_id.overwrite_company_settings", "=", False),
            "|",
            ("approval_requested", "=", True),
            ("completed_approval_process_id", "!=", False),
        ]

    def _compute_has_invoices_for_reset(self):
        for company in self:
            domain = self._get_domain_invoices_for_reset(company.id)
            invoices = self.env["account.invoice"].search(domain)
            company.has_invoices_for_reset = True if invoices else False

    def action_reset_journal_draft_invoices(self):
        msg = _("Aproval process resetted.")
        domain = self._get_domain_invoices_for_reset(self.ids)
        invoices = self.env["account.invoice"].search(domain)
        invoices.write(
            {
                "approval_requested": False,
                "completed_approval_process_id": False,
            }
        )
        for invoice in invoices:
            invoice.message_post(body=msg)
