import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """
    Initializing column custom_rate on table account_move
    for the improvement in performance to avoid long
    duration in databases with thousand of moves
    """
    _logger.info("Initializing column custom_rate on table account_move")
    sql.create_column(
        cr=env.cr,
        tablename="account_move",
        columnname="custom_rate",
        columntype="numeric",
        comment="Custom Rate",
    )
    env.cr.execute(
        """
        UPDATE
            account_move
        SET
            custom_rate = 1.0
        """
    )
