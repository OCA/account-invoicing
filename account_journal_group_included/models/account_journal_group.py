#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountJournalGroup(models.Model):
    _inherit = "account.journal.group"

    included_journal_ids = fields.Many2many(
        check_company=True,
        comodel_name="account.journal",
        compute="_compute_included_journal_ids",
        inverse="_inverse_included_journal_ids",
        string="Included Journals",
    )

    def _get_journals_by_company(self):
        """Get journals grouped by the companies in the groups `self`."""
        journal_groups = self.env["account.journal"].read_group(
            [
                ("company_id", "in", self.company_id.ids),
            ],
            [
                "id",
            ],
            [
                "company_id",
            ],
        )
        company_to_journals = {
            self.env["res.company"]
            .browse(journal_group["company_id"][0]): self.env["account.journal"]
            .search(journal_group["__domain"])
            for journal_group in journal_groups
        }
        return company_to_journals

    @api.depends(
        "company_id",
        "excluded_journal_ids",
    )
    def _compute_included_journal_ids(self):
        company_to_journals = self._get_journals_by_company()
        for group in self:
            group.included_journal_ids = (
                company_to_journals[group.company_id] - group.excluded_journal_ids
            )

    def _inverse_included_journal_ids(self):
        company_to_journals = self._get_journals_by_company()
        for group in self:
            group.excluded_journal_ids = (
                company_to_journals[group.company_id] - group.included_journal_ids
            )
