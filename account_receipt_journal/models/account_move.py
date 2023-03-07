from odoo import _, api, exceptions, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("company_id", "invoice_filter_type_domain", "move_type")
    def _compute_suitable_journal_ids(self):
        res = super()._compute_suitable_journal_ids()
        for m in self:
            dedicated_journals = m.suitable_journal_ids.filtered(
                lambda j: j.receipts == m.move_type in {"out_receipt", "in_receipt"}
            )
            # Suitable journals dedicated to receipts if exists
            m.suitable_journal_ids = dedicated_journals or m.suitable_journal_ids
        return res

    @api.model
    def _search_default_receipt_journal(self, journal_types):
        company_id = self.env.context.get("default_company_id", self.env.company.id)
        currency_id = self.env.context.get("default_currency_id")
        domain = [
            ("company_id", "=", company_id),
            ("type", "in", journal_types),
            ("receipts", "=", True),
        ]
        journal = None
        if currency_id:
            journal = self.env["account.journal"].search(
                domain + [("currency_id", "=", currency_id)], limit=1
            )
        if not journal:
            journal = self.env["account.journal"].search(domain, limit=1)
        return journal

    @api.model
    def _search_default_journal(self, journal_types):
        journal = super()._search_default_journal(journal_types)
        move_type = self.env.context.get("default_move_type")
        # We can assume that if move_type is not in receipts, a journal without
        # receipts it's coming because of the Journal constraint
        if move_type not in {"in_receipt", "out_receipt"} or journal.receipts:
            return journal
        return self._search_default_receipt_journal(journal_types) or journal

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

    @api.constrains("move_type", "journal_id")
    def _check_receipts_journal(self):
        """Ensure that Receipt Journal is only used in Receipts
        if exists Receipt Journals for its type"""
        aj_model = self.env["account.journal"]
        receipt_domain = [("receipts", "=", True)]
        has_in_rjournals = aj_model.search([("type", "=", "purchase")] + receipt_domain)
        has_out_rjournals = aj_model.search([("type", "=", "sale")] + receipt_domain)
        for move in self:
            is_rj = move.journal_id.receipts
            if move.move_type not in {"in_receipt", "out_receipt"} and is_rj:
                raise exceptions.ValidationError(
                    _("Receipt Journal is restricted to Receipts")
                )
            elif move.move_type == "in_receipt" and not is_rj and has_in_rjournals:
                raise exceptions.ValidationError(
                    _(
                        "Purchase Receipt must use a Receipt Journal because "
                        "there is already a Receipt Journal for Purchases"
                    )
                )
            elif move.move_type == "out_receipt" and not is_rj and has_out_rjournals:
                raise exceptions.ValidationError(
                    _(
                        "Sale Receipt must use a Receipt Journal because "
                        "there is already a Receipt Journal for Sales"
                    )
                )
