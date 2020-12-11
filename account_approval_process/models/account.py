# Copyright (C) 2020 - TODAY, Elego Software Solutions GmbH, Berlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, exceptions, fields, models, _

_logger = logging.getLogger(__name__)

INVOICE_TYPES = {
    "sale": ("out_invoice", "out_refund"),
    "purchase": ("in_invoice", "in_refund"),
}


class AccountJournal(models.Model):
    _inherit = "account.journal"

    overwrite_company_settings = fields.Boolean()

    has_invoices_for_reset = fields.Boolean(
        compute="_compute_has_invoices_for_reset",
    )

    company_account_approval_process_ids = fields.One2many(
        comodel_name="account.approval.process",
        compute="_compute_company_account_approval_process_ids",
        string="Company Approval processes",
    )

    journal_account_approval_process_ids = fields.One2many(
        comodel_name="account.approval.process",
        inverse_name="journal_id",
        string="Journal Approval processes",
        context={
            "active_test": False,
        },
    )

    @api.constrains("journal_account_approval_process_ids")
    def _check_validation_amount(self):
        def get_type_str(invoice_type):
            processes = self.journal_account_approval_process_ids
            return dict(processes.fields_get()["invoice_type"]["selection"]).get(
                invoice_type
            )

        processes = self.journal_account_approval_process_ids
        msgs = []
        for invoice_type in set(processes.mapped("invoice_type")):
            if processes and not processes.filtered(
                lambda rc: rc.invoice_type == invoice_type
                and rc.validation_amount_to == -1.0
            ):
                msg = _(
                    "At least one step of the type '{type}' must have the value -1 for"
                    " unlimited at the field 'Amount (to)'."
                ).format(type=get_type_str(invoice_type))
                msgs.append(msg)

        types = INVOICE_TYPES.get(self.type)
        if processes and processes.filtered(lambda rc: rc.invoice_type not in types):
            types = [get_type_str(t) for t in INVOICE_TYPES.get(self.type)]
            msg = _(
                "A type is not allowed; only the following types are permitted for "
                "journal '{journal}':\n{types}"
            ).format(
                type=get_type_str(self.type), journal=self.name, types="\n".join(types)
            )
            msgs.append(msg)

        if msgs:
            raise exceptions.ValidationError("\n".join(msgs))

    def _get_domain_invoices_for_reset(self, invoice_type, ids):
        domain = [
            "&",
            ("type", "in", INVOICE_TYPES.get(invoice_type)),
            "&",
            ("state", "=", "draft"),
            "&",
            ("journal_id", "=" if isinstance(ids, int) else "in", ids),
            "&",
            ("journal_id.overwrite_company_settings", "=", True),
            "|",
            ("approval_requested", "=", True),
            ("completed_approval_process_id", "!=", False),
        ]
        _logger.debug("_get_domain_invoices_for_reset: domain=%s", domain)
        return domain

    def _compute_company_account_approval_process_ids(self):
        for journal in self:
            types = INVOICE_TYPES.get(journal.type)
            lines = journal.company_id.account_approval_process_ids.filtered(
                lambda i: i.company_id == journal.company_id
                and (types and i.invoice_type in types or not types)
            )
            journal.company_account_approval_process_ids = lines

    def _compute_has_invoices_for_reset(self):
        for journal in self:
            domain = journal._get_domain_invoices_for_reset(journal.type, journal.id)
            invoices = self.env["account.invoice"].search(domain)
            journal.has_invoices_for_reset = True if invoices else False

    def action_copy_company_processes(self):
        for journal in self:
            types = INVOICE_TYPES.get(journal.type)
            for process in journal.company_account_approval_process_ids.filtered(
                lambda p: p.invoice_type in types
            ):
                process.copy(
                    {
                        "company_id": False,
                        "journal_id": journal.id,
                    }
                )

    def action_reset_journal_draft_invoices(self):
        msg = _("Aproval process resetted.")
        invoices = self.env["account.invoice"]
        for invoice_type in self.mapped("type"):
            journals = self.filtered(lambda j: j.type == invoice_type)
            domain = self._get_domain_invoices_for_reset(invoice_type, journals.ids)
            invoices |= self.env["account.invoice"].search(domain)
        invoices.write(
            {
                "approval_requested": False,
                "completed_approval_process_id": False,
            }
        )
        for invoice in invoices:
            invoice.message_post(body=msg)
