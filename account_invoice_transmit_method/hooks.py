# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


def pre_init_hook(env):
    env.cr.execute(
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS transmit_method_id INTEGER;
        """,
    )
