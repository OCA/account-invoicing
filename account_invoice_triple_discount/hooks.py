# Copyright 2024-Today - Sylvain Le GAL (GRAP)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    _logger.info("Initializing column discount1 on table account_move_line")
    env.cr.execute(
        """
            UPDATE account_move_line
            SET discount1 = discount
            WHERE discount != 0
        """
    )
    # if discounts are : 10% - 20% - 30% main discount is : 49.6 %
    # if discounts are : 05% - 09% - 13% main discount is : 24.7885 %
    env.cr.execute(
        """
        UPDATE account_move_line
        SET discount = 100 * (
            1 - (
                    (100 - COALESCE(discount1, 0.0)) / 100
                    * (100 - COALESCE(discount2, 0.0)) / 100
                    * (100 - COALESCE(discount3, 0.0)) / 100
                )
        );
        """
    )
