# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from logging import getLogger

from odoo import SUPERUSER_ID, api

_logger = getLogger(__name__)


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        force_compute_original_partners(env)


def force_compute_original_partners(env):
    """Force compute original partners.

    Since field `original_partner_ids` is not automatically computed upon
    module installation, we need to compute it manually on existing records.

    :param env: an Odoo Environment instance
    """
    domain = [("move_type", "=", "out_invoice")]
    invs = env["account.move"].search(domain)
    _logger.info("Force-compute original partners on %s invoices" % len(invs))
    invs._compute_original_partner_ids()
