# Copyright 2024 Camptocamp SA
# Copyright 2026 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import SUPERUSER_ID
from odoo.api import Environment
from odoo.tools import column_exists

USE_OPENUPGRADE = False
USE_ODOOUPGRADE = False

try:
    from odoo.upgrade import util

    USE_ODOOUPGRADE = True
except ImportError:
    try:
        from openupgradelib import openupgrade

        USE_OPENUPGRADE = True
    except ImportError as err:
        raise ImportError(
            "This migration script requires openupgradelib or odoo.upgrade.util.\n"
            "Please install one of these libraries to proceed with the migration.\n"
            "For better performances, it is recommended to use odoo.upgrade.util.\n"
            "See https://github.com/odoo/upgrade-util/"
        ) from err


_logger = logging.getLogger(__name__)


def migrate_discount_to_discount1(env):
    if not column_exists(env.cr, "account_move_line", "discount1"):
        env.cr.execute(
            """
            ALTER TABLE account_move_line
            ADD COLUMN discount1 numeric;
            """
        )
        _logger.info("Added column 'discount1' to 'account_move_line'")

    query = """
        UPDATE account_move_line
        SET discount1 = discount,
        """

    if "discount_fixed" not in env.registry.models["account.move.line"]._fields:
        query += """
            discount = 100 * (
                1 - (
                        (100 - COALESCE(discount, 0.0)) / 100
                        * (100 - COALESCE(discount2, 0.0)) / 100
                        * (100 - COALESCE(discount3, 0.0)) / 100
                    )
            )
            """

    else:
        # don't touch lines with fixed discount
        # We don't use a WHERE clause since the explode_query_range will
        # add a WHERE clause with an id range, so we need to express
        # the condition in a way that is compatible with that.
        query += """
            discount =
            CASE
                WHEN discount_fixed == 0 THEN
                    100 * (
                        1 - (
                                (100 - COALESCE(discount, 0.0)) / 100
                                * (100 - COALESCE(discount2, 0.0)) / 100
                                * (100 - COALESCE(discount3, 0.0)) / 100
                            )
                    )
                ELSE discount
            END
            """

    if USE_OPENUPGRADE:
        openupgrade.logged_query(env.cr, query)

    else:
        util.parallel_execute(
            env.cr, util.explode_query_range(env.cr, query, table="account_move_line")
        )


def migrate(cr, version):
    env = Environment(cr, SUPERUSER_ID, {})
    migrate_discount_to_discount1(env)
