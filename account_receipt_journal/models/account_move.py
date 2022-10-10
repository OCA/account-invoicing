from odoo import api, models


class Move(models.Model):
    _inherit = "account.move"

    @api.model
    def _search_default_receipt_journal(self, journal_types):
        company_id = self._context.get("default_company_id", self.env.company.id)
        domain = [
            ("company_id", "=", company_id),
            ("type", "in", journal_types),
            ("receipts", "=", True),
        ]
        journal = None
        if self._context.get("default_currency_id"):
            currency_domain = domain + [
                ("currency_id", "=", self._context["default_currency_id"])
            ]
            journal = self.env["account.journal"].search(currency_domain, limit=1)
        if not journal:
            journal = self.env["account.journal"].search(domain, limit=1)
        return journal

    @api.model
    def _search_default_journal(self, journal_types):
        journal = super(Move, self)._search_default_journal(journal_types)
        default_move_type = self.env.context.get("default_move_type")
        if not journal.receipts and default_move_type in ("in_receipt", "out_receipt"):
            receipt_journal = self._search_default_receipt_journal(journal_types)
            if receipt_journal:
                journal = receipt_journal
        return journal
