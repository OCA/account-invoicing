# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


@openupgrade.logging()
def compute_discount(env):
    move_lines_to_compute = env["account.move.line"].search(
        [
            "|",
            "|",
            ("discount1", "!=", 0),
            ("discount2", "!=", 0),
            ("discount3", "!=", 0),
        ]
    )
    for line in move_lines_to_compute:
        discount = line._get_aggregated_discount_from_values(
            {fname: line[fname] for fname in line._get_multiple_discount_field_names()}
        )
        rounded_discount = line._fields["discount"].convert_to_column(discount, line)
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_move_line
            SET discount = %s
            WHERE id = %s;
        """,
            tuple(
                [
                    rounded_discount,
                    line.id,
                ]
            ),
        )


@openupgrade.migrate()
def migrate(env, version):
    compute_discount(env)
