# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import openupgrade


def migrate_discount_to_discount1():
    openupgrade.add_fields(
        [
            (
                "discount1",
                "account.move.line",
                "account_move_line",
                "float",
                "numeric",
                "account_invoice_triple_discount",
                0.0,
            )
        ]
    )
    openupgrade.logged_query(
        """
        UPDATE account_move_line
        SET discount1 = discount;
        """
    )


def migrate(cr, version):
    migrate_discount_to_discount1()
