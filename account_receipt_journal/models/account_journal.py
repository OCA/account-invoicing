from odoo import _, api, exceptions, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    receipts = fields.Boolean(
        string="Exclusive to Receipts",
        help="If checked, this journal will be used by default for receipts "
        "and only can be used for receipts.",
    )

    def _get_move_action_context(self):
        res = super()._get_move_action_context()
        ctx = self._context.copy()
        journal = self or self.browse(ctx["default_journal_id"])
        if not journal or not journal.receipts:
            return res
        if journal.type == "sale":
            res["default_move_type"] = "out_receipt"
        elif journal.type == "purchase":
            res["default_move_type"] = "in_receipt"
        return res

    def open_action(self):
        """Create a new Receipt from the Dashboard
        Button link in name of journal
        """
        res = super().open_action()
        if not self.receipts:
            return res
        if self.type == "sale":
            res["context"]["default_move_type"] = "out_receipt"
            res["domain"] = [("move_type", "=", "out_receipt")]
        elif self.type == "purchase":
            res["context"]["default_move_type"] = "in_receipt"
            res["domain"] = [("move_type", "=", "in_receipt")]
        return res

    @api.constrains("sequence", "type", "receipts", "company_id")
    def _check_receipts_sequence(self):
        """Ensure that journals with receipts checked, are on a higher sequence
        that the rest of journals of the same type"""
        for receipt_journal in self.filtered("receipts"):
            journals = self.search(
                [
                    ("type", "=", receipt_journal.type),
                    ("receipts", "=", False),
                    # ("sequence", "<", journal.sequence),
                    ("id", "!=", receipt_journal.id),
                    ("company_id", "=", receipt_journal.company_id.id),
                ]
            )
            if not journals:
                continue
            previous_sequence_journals = journals.filtered(
                lambda j, r=receipt_journal: j.sequence < r.sequence
            )
            if not previous_sequence_journals:
                raise exceptions.ValidationError(
                    _(
                        "The sequence of the journal '%s' must be higher than "
                        "the sequence of the other journals of the same type."
                    )
                    % receipt_journal.name
                )
