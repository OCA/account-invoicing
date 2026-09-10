# Copyright 2026 (APSL - Nagarro) Sara Zambrano
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)

# Attachment extensions considered "valid" to digitize an invoice.
VALID_ATTACHMENT_EXTENSIONS = (".pdf", ".xml")

# account_invoice_extract / iap_extract states considered a digitization
# (OCR) failure. That module is optional: not every database has it
# installed, so every method below that touches ``extract_state`` first
# checks that the field actually exists on the model.
OCR_FAILED_STATES = ("error_status", "not_enough_credit")


class AccountMove(models.Model):
    _inherit = "account.move"

    email_status = fields.Selection(
        selection=[
            ("missing_attachment", "Received without attachment"),
            ("resolved", "Resolved"),
        ],
        string="Email status",
        copy=False,
        index=True,
        help="Status of the traceability of the inbound email that "
        "originated this move.",
    )
    email_attachment_missing = fields.Boolean(
        string="Received without attachment",
        default=False,
        copy=False,
        index=True,
        help="The source email did not carry any valid PDF/XML attachment "
        "to digitize. This record was created only to keep track of the "
        "contact that wrote to the journal alias.",
    )
    email_from_raw = fields.Char(
        string="Original sender",
        copy=False,
        help="Sender email exactly as received in the 'From' header, "
        "useful when the contact could not be identified automatically.",
    )
    email_issue_resolved = fields.Boolean(
        string="Resolved",
        default=False,
        copy=False,
        index=True,
        help="Set by the user once this move, originally received "
        "without an attachment, has been completed or fixed manually. "
        "Once set, it no longer appears in the Failed Invoices menu.",
    )
    ocr_failed = fields.Boolean(
        string="Digitization failed",
        default=False,
        copy=False,
        help="The attachment arrived correctly but the OCR/digitization "
        "process could not be completed or was inconclusive. Only "
        "relevant when an invoice digitization module (e.g. "
        "account_invoice_extract) is installed.",
    )
    ocr_failure_reason = fields.Char(
        string="Digitization failure reason",
    )

    def action_mark_email_issue_resolved(self):
        """Button shown on the form view when the move is flagged as
        'Received without attachment'. The user triggers it once the
        record has been completed or fixed manually, to remove it from
        the Failed Invoices menu."""
        for move in self:
            move.email_status = "resolved"
            move.email_issue_resolved = True
            move.email_attachment_missing = False
            pending_activities = move.activity_ids.filtered(
                lambda a: a.summary
                == "Review invoice received by email without attachment"
            )
            if pending_activities:
                pending_activities.action_feedback(
                    feedback="Manually marked as resolved by the user."
                )
            move.message_post(
                body=self.env._(
                    "This move was marked as <b>resolved</b>: it will no "
                    "longer appear in the Failed Invoices menu."
                )
            )
        return True

    def action_undo_email_issue_resolved(self):
        """Revert the 'Resolved' status in case it was set by mistake."""
        return self.write({"email_status": "missing_attachment"})

    @api.model
    def _routing_check_route(self, message, message_dict, route, raise_exception=True):
        """Odoo's native ``account.move._routing_check_route`` bounces the
        incoming email and discards the route (``return ()``) whenever it
        has no attachment at all, before ``message_new`` is ever reached.
        Without this override, ``account.move`` is never created when the
        attachment is missing: it is not a bug in our ``message_new``, our
        code simply never gets called.

        To keep traceability, when the route targets ``account.move`` and
        there are no attachments, we pass the native check a COPY of
        ``message_dict`` with a "decoy" attachment (only so it does not
        trigger the bounce). The ORIGINAL ``message_dict`` (without that
        decoy) is still used for the rest of the processing, so no fake
        ``ir.attachment`` is ever created: the decoy only lives within this
        call chain.
        """
        if (
            route[0] == "account.move"
            and len(message_dict.get("attachments") or []) < 1
        ):
            journal = self._routing_get_journal_from_route(route)
            if journal and journal.type == "purchase":
                message_dict = dict(message_dict)
                message_dict["attachments"] = [
                    ("__no_attachment__.placeholder", b"", {})
                ]
        return super()._routing_check_route(
            message, message_dict, route, raise_exception=raise_exception
        )

    @api.model
    def _routing_get_journal_from_route(self, route):
        """route es una tupla (model, thread_id, custom_values, uid, alias).
        custom_values normalmente incluye journal_id cuando el alias
        apunta a account.move."""
        custom_values = route[2] if len(route) > 2 else {}
        journal_id = (custom_values or {}).get("journal_id")
        if journal_id:
            return self.env["account.journal"].browse(journal_id)
        return self.env["account.journal"]

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """Intercept the creation of an ``account.move`` from an inbound
        email to a journal alias.

        - If the email carries a PDF/XML attachment: native Odoo behavior
          is respected (creates the draft and follows the normal flow,
          including OCR/digitization if configured).
        - If it does NOT carry a valid attachment: the record is created
          anyway (to keep traceability), but flagged as "missing
          attachment", the sending contact is looked up, and a manual
          review activity is scheduled.
        """
        attachments = msg_dict.get("attachments") or []
        has_valid_attachment = any(
            (self._email_attachment_name(att) or "")
            .lower()
            .endswith(VALID_ATTACHMENT_EXTENSIONS)
            for att in attachments
        )

        journal_id = (custom_values or {}).get("journal_id")
        journal = self.env["account.journal"].browse(journal_id) if journal_id else None
        is_purchase_journal = bool(journal and journal.type == "purchase")

        if has_valid_attachment or not is_purchase_journal:
            return super().message_new(msg_dict, custom_values)

        email_from = msg_dict.get("from") or ""
        partner = self._email_find_partner(email_from)

        custom_values = dict(custom_values or {})
        if partner:
            custom_values["partner_id"] = partner.id

        move = super().message_new(msg_dict, custom_values)

        move.write(
            {
                "email_status": "missing_attachment",
                "email_from_raw": email_from,
                "email_attachment_missing": True,
            }
        )
        if partner and not move.partner_id:
            move.partner_id = partner.id

        _logger.info(
            "Email received on journal alias without a valid attachment. "
            "from=%s move_id=%s journal_id=%s partner=%s",
            email_from,
            move.id,
            move.journal_id.id,
            partner.display_name if partner else "Not identified",
        )

        move._email_attachment_missing_notify(email_from, partner)
        return move

    @api.model
    def _email_attachment_name(self, attachment):
        """``attachments`` can be a ``(name, content, info)`` tuple or a
        ``_Attachment`` namedtuple depending on the version; normalize the
        access to the file name so we do not depend on its exact shape."""
        if not attachment:
            return False
        if hasattr(attachment, "fname"):
            return attachment.fname
        if isinstance(attachment, (list, tuple)) and attachment:
            return attachment[0]
        return False

    def _email_find_partner(self, email_from):
        """Try to identify the contact (customer/vendor) from the sender
        email of the inbound message.

        1) Exact match on the normalized email.
        2) If there is no exact match, look for an already loaded vendor
           contact sharing the same domain.
        """
        parsed = tools.email_split(email_from)
        email = parsed[0] if parsed else False
        if not email:
            return self.env["res.partner"]

        normalized = tools.email_normalize(email)
        partner = self.env["res.partner"].search(
            [("email_normalized", "=", normalized)], limit=1
        )
        if partner:
            return partner

        domain = email.split("@")[-1] if "@" in email else False
        if not domain:
            return self.env["res.partner"]

        partner = self.env["res.partner"].search(
            [("email", "like", f"@{domain}"), ("supplier_rank", ">", 0)], limit=1
        )
        if partner:
            return partner

        return self.env["res.partner"].search(
            [("email", "like", f"@{domain}")], limit=1
        )

    def _email_attachment_missing_notify(self, email_from, partner):
        """Schedule an activity so someone reviews the case manually."""
        self.ensure_one()
        responsible = self.journal_id.activity_user_id or self.env.user

        note = (
            f"The email from <b>{email_from or 'unknown sender'}</b> arrived "
            f"on the alias of journal <b>{self.journal_id.display_name}</b> "
            f"without any PDF/XML attachment, so it could not be digitized "
            f"automatically."
        )
        if partner:
            note += (
                f"<br/>Contact automatically identified: <b>{partner.display_name}</b>."
            )
        else:
            note += (
                "<br/>The contact could not be identified automatically, "
                "please review manually."
            )

        self.activity_schedule(
            "mail.mail_activity_data_todo",
            summary="Review invoice received by email without attachment",
            note=note,
            user_id=responsible.id,
        )

    @api.model
    def _cron_check_ocr_failures(self):
        """Periodically check moves whose digitization (OCR) process ended
        in error, and flag/notify them the same way as the "email without
        attachment" case.

        This is a no-op when no invoice digitization module (e.g. the
        Enterprise ``account_invoice_extract``) is installed, since the
        ``extract_state`` field would not exist on ``account.move``.
        """
        if "extract_state" not in self._fields:
            _logger.info(
                "No invoice digitization module installed (missing "
                "'extract_state' field on account.move): skipping OCR "
                "failure check."
            )
            return self.browse()

        domain = [
            ("extract_state", "in", OCR_FAILED_STATES),
            ("ocr_failed", "=", False),
            ("journal_id.type", "=", "purchase"),
        ]
        failed_moves = self.search(domain)
        for move in failed_moves:
            move.ocr_failed = True
            move.ocr_failure_reason = dict(move._fields["extract_state"].selection).get(
                move.extract_state, move.extract_state
            )
            move._ocr_failure_notify()
        return failed_moves

    def _ocr_failure_notify(self):
        self.ensure_one()
        responsible = self.journal_id.activity_user_id or self.env.user
        note = (
            f"Automatic digitization (OCR) of this invoice could not be "
            f"completed.<br/>Reason: <b>{self.ocr_failure_reason or 'unknown'}</b>."
            f"<br/>Please review the attachment and, if applicable, enter "
            f"the data manually."
        )
        self.activity_schedule(
            "mail.mail_activity_data_todo",
            summary="Review invoice with failed digitization",
            note=note,
            user_id=responsible.id,
        )
