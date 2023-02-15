# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _initialize_restocking_fee_product(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Initialize restocking fee product on companies")
    restocking_fee_product = env.ref(
        "sale_stock_restocking_fee_invoicing.product_restocking_fee"
    )
    env["res.company"].search([]).write(
        {"restocking_fee_product_id": restocking_fee_product.id}
    )


def post_init_hook(cr, registry):
    _initialize_restocking_fee_product(cr)
