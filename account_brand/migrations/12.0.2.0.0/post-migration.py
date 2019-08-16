# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Move sale brand to res.brand model")
    cr.execute("""
        UPDATE account_invoice SET brand_id = brand.id
        FROM res_brand brand
        WHERE brand.partner_id=brand_id_tmp""")
    cr.execute("""ALTER TABLE account_invoice DROP COLUMN brand_id_tmp""")
