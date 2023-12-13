# Copyright 2024-Today - Sylvain Le GAL (GRAP)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    _logger.info("Initializing column discount1 on table account_move_line")
    if "discount_fixed" not in env["account.move.line"]._fields:
        env.cr.execute(
            """
                UPDATE account_move_line
                SET discount1 = discount
                WHERE discount != 0
            """
        )
    else:
        env.cr.execute(
            """
                UPDATE account_move_line
                SET discount1 = discount
                WHERE discount != 0 AND discount_fixed = 0
            """
        )
