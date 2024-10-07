#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import first
from odoo.tests import TransactionCase


class TestAccountJournalGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.journal_group = cls.env["account.journal.group"].create(
            {
                "name": "Test journal group",
            }
        )

    def test_exclude_journals_sync(self):
        """Exclude a journal: it is removed from the included journals."""
        # Arrange
        journal_group = self.journal_group
        grouped_journals = (
            journal_group.included_journal_ids + journal_group.excluded_journal_ids
        )
        journal_group.included_journal_ids = grouped_journals
        included_journal = first(grouped_journals)
        # pre-condition
        self.assertNotIn(included_journal, journal_group.excluded_journal_ids)
        self.assertIn(included_journal, journal_group.included_journal_ids)

        # Act
        journal_group.excluded_journal_ids += included_journal

        # Assert
        self.assertIn(included_journal, journal_group.excluded_journal_ids)
        self.assertNotIn(included_journal, journal_group.included_journal_ids)

    def test_include_journals_sync(self):
        """Include a journal: it is removed from the excluded journals."""
        # Arrange
        journal_group = self.journal_group
        grouped_journals = (
            journal_group.included_journal_ids + journal_group.excluded_journal_ids
        )
        journal_group.excluded_journal_ids = grouped_journals
        excluded_journal = first(grouped_journals)
        # pre-condition
        self.assertIn(excluded_journal, journal_group.excluded_journal_ids)
        self.assertNotIn(excluded_journal, journal_group.included_journal_ids)

        # Act
        journal_group.included_journal_ids += excluded_journal

        # Assert
        self.assertNotIn(excluded_journal, journal_group.excluded_journal_ids)
        self.assertIn(excluded_journal, journal_group.included_journal_ids)
