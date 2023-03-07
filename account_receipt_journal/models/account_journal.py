from odoo import _, api, exceptions, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    receipts = fields.Boolean(
        string="Exclusive to Receipts",
        help="If checked, this journal will be used by default for receipts "
        "and only can be used for receipts.",
    )

    def action_create_new(self):
        """Create a new Receipt from the Dashboard"""
        res = super().action_create_new()
        if not self.receipts:
            return res
        res["name"] = _("Create receipt")
        if self.type == "sale":
            res["context"]["default_move_type"] = "out_receipt"
        elif self.type == "purchase":
            res["context"]["default_move_type"] = "in_receipt"
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
                lambda j: j.sequence < receipt_journal.sequence
            )
            if not previous_sequence_journals:
                raise exceptions.ValidationError(
                    _(
                        "The sequence of the journal '%s' must be higher than "
                        "the sequence of the other journals of the same type."
                    )
                    % receipt_journal.name
                )
