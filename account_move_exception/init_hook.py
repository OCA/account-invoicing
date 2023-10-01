# Copyright 2021 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools.sql import column_exists

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.
    """
    store_exception_fields(cr)


def store_exception_fields(cr):
    if not column_exists(cr, "account_move", "main_exception_id"):
        logger.info("Creating field main_exception_id on account_move")
        cr.execute(
            """
            ALTER TABLE account_move
            ADD COLUMN main_exception_id int;
            COMMENT ON COLUMN account_move.main_exception_id IS 'Main Exception';
            """
        )
    if not column_exists(cr, "account_move", "ignore_exception"):
        logger.info("Creating field ignore_exception on account_move")
        cr.execute(
            """
            ALTER TABLE account_move
            ADD COLUMN ignore_exception boolean;
            COMMENT ON COLUMN account_move.ignore_exception IS 'Ignore Exceptions';
            """
        )
