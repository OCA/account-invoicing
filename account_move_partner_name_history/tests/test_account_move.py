#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
import operator
from functools import reduce

from dateutil.relativedelta import relativedelta

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.partner_name_history.tests.common import (
    _get_name_from_date,
    _set_partner_name,
)


@tagged("post_install", "-at_install")
class TestAccountMove(AccountTestInvoicingCommon):
    def test_context_use_partner_name_history(self):
        """Context key `use_partner_name_history` allows to return
        the name according to the partner's history."""
        # Arrange
        one_day = relativedelta(days=1)
        partner = self.partner_a
        original_partner_name = partner.name
        change_dates = [
            datetime.date(2019, 1, 1),
            datetime.date(2020, 1, 1),
        ]
        date_to_names = {date: _get_name_from_date(date) for date in change_dates}
        for change_date, name in date_to_names.items():
            _set_partner_name(
                partner,
                name,
                date=change_date,
            )

        # Act
        moves = reduce(
            operator.ior,
            [
                self.init_invoice(
                    "out_invoice",
                    partner=partner,
                    invoice_date=date,
                )
                for date in [
                    change_dates[0] - one_day,
                    change_dates[0] + one_day,
                    change_dates[1] - one_day,
                    change_dates[1] + one_day,
                ]
            ],
        )

        # Assert
        last_partner_name = partner.name
        one_day = relativedelta(days=1)
        date_to_expected_name = {
            change_dates[0] - one_day: original_partner_name,
            change_dates[0] + one_day: _get_name_from_date(change_dates[0]),
            change_dates[1] - one_day: _get_name_from_date(change_dates[0]),
            change_dates[1] + one_day: last_partner_name,
        }
        moves_with_ctx = moves.with_context(use_partner_name_history=True)
        for record_date, expected_name in date_to_expected_name.items():
            # Without context, the record has the latest name of the partner
            partner.invalidate_recordset(
                fnames=[
                    "name",
                ],
            )
            move = moves.filtered(lambda m: m.invoice_date == record_date)
            self.assertEqual(last_partner_name, move.partner_id.name)

            # With context, the partner's name is the one at the specific date
            move_with_ctx = moves_with_ctx.filtered(
                lambda m: m.invoice_date == record_date
            )
            self.assertEqual(expected_name, move_with_ctx.partner_id.name)

    def test_not_invoice_partner_name(self):
        """Moves that are not invoices use account.move.date."""
        # Arrange
        one_day = relativedelta(days=1)
        partner = self.partner_a
        original_partner_name = partner.name
        new_partner_name, change_date = "New name", datetime.date(2020, 1, 1)
        _set_partner_name(partner, new_partner_name, date=change_date)

        # Act
        moves = (
            self.env["account.move"]
            .create(
                [
                    {
                        "move_type": "entry",
                        "partner_id": partner.id,
                        "date": date,
                    }
                    for date in [
                        change_date - one_day,
                        change_date + one_day,
                    ]
                ]
            )
            .with_context(
                use_partner_name_history=True,
            )
        )

        # Assert
        old_move, new_move = moves.sorted("date")

        self.assertFalse(old_move.invoice_date)
        self.assertEqual(old_move.partner_id.name, original_partner_name)

        self.assertFalse(new_move.invoice_date)
        self.assertEqual(new_move.partner_id.name, new_partner_name)

    def test_empty_invoice_and_line(self):
        """The name of the partner of empty moves (and lines) is empty."""
        # Arrange
        empty_move = (
            self.env["account.move"]
            .browse()
            .with_context(
                use_partner_name_history=True,
            )
        )
        empty_move_line = empty_move.line_ids
        # pre-condition
        self.assertFalse(empty_move)
        self.assertFalse(empty_move_line)

        # Assert
        self.assertFalse(empty_move.partner_id.name)
        self.assertFalse(empty_move_line.partner_id.name)
