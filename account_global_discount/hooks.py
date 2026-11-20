from odoo.tools.sql import column_exists


def _pre_init_global_discount_fields(env):
    if not column_exists(env.cr, "account_move", "amount_global_discount"):
        env.cr.execute(
            """
                ALTER TABLE "account_move"
                ADD COLUMN "amount_global_discount" double precision DEFAULT 0
            """
        )
        env.cr.execute(
            """
        ALTER TABLE "account_move" ALTER COLUMN "amount_global_discount" DROP DEFAULT
        """
        )
    if not column_exists(
        env.cr, "account_move", "amount_untaxed_before_global_discounts"
    ):
        env.cr.execute(
            """
                ALTER TABLE "account_move"
                ADD COLUMN "amount_untaxed_before_global_discounts" double precision
            """
        )
        env.cr.execute(
            """
        update account_move set amount_untaxed_before_global_discounts = amount_untaxed
        """
        )
