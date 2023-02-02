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

    def _get_journal_types(self, move_type):
        if move_type in self.get_sale_types(include_receipts=True):
            journal_types = ["sale"]
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_types = ["purchase"]
        else:
            journal_types = self.env.context.get(
                "default_move_journal_types", ["general"]
            )
        return journal_types

    @api.model
    def _update_receipts_journal(self, vals_list):
        """
        Update `vals_list` in place to set journal_id to the receipt journal
        when move_type is receipt.

        Model defaults are also considered it move_type or journal_id
        are not in a `vals_list`.
        """
        defaults = self.default_get(["journal_id", "move_type"])
        default_journal = defaults.get("journal_id")
        default_move_type = defaults.get("move_type")
        for vals in vals_list:
            move_type = vals.get("move_type", default_move_type)
            if move_type in ("in_receipt", "out_receipt"):
                selected_journal_id = vals.get("journal_id", default_journal)
                selected_journal = self.env["account.journal"].browse(
                    selected_journal_id
                )
                if not selected_journal.receipts:
                    journal_types = self._get_journal_types(move_type)
                    receipt_journal = self._search_default_receipt_journal(
                        journal_types
                    )
                    if receipt_journal:
                        vals["journal_id"] = receipt_journal.id

    @api.model_create_multi
    def create(self, vals_list):
        self._update_receipts_journal(vals_list)
        return super().create(vals_list)
