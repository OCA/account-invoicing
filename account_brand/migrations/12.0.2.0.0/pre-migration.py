# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Move invoice brand to res.brand model")
    cr.execute(
        """ALTER TABLE account_invoice
        ADD COLUMN brand_id_tmp INTEGER"""
    )
    cr.execute("""UPDATE account_invoice  SET brand_id_tmp = brand_id""")
    cr.execute("""ALTER TABLE account_invoice DROP COLUMN brand_id""")
