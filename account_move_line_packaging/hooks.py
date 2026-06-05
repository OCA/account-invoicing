# Copyright 2026 ACSONE SA/NV
# Copyright 2026 BCIM

from odoo.tools.sql import column_exists


def pre_init_hook(cr):
    if not column_exists(cr, "account_move_line", "product_packaging_id"):
        cr.execute(
            """
            ALTER TABLE account_move_line
            ADD COLUMN product_packaging_id integer
            """
        )

    if not column_exists(cr, "account_move_line", "product_packaging_qty"):
        cr.execute(
            """
            ALTER TABLE account_move_line
            ADD COLUMN product_packaging_qty numeric
            """
        )
